import os
from io import BytesIO

from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

from .models import MedicationHistory


LOGO_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'static', 'medalert_logo.png'
)

AZUL = colors.HexColor('#1d4ed8')
CORAL = colors.HexColor('#fb923c')
GRIS = colors.HexColor('#6b7280')
GRIS_CLARO = colors.HexColor('#f3f4f6')

GENERO_LEGIBLE = {
    'masculino': 'Masculino',
    'femenino': 'Femenino',
    'prefiero_no_decir': 'Prefiero no decir',
}

TIPO_CITA_LEGIBLE = {
    'consulta': 'Consulta con especialista',
    'examen': 'Examen médico',
    'terapia': 'Terapia física',
    'cirugia': 'Cirugía programada',
}

ESTADO_CITA_LEGIBLE = {
    'pendiente': 'Pendiente',
    'cumplida': 'Cumplida',
    'cancelada': 'Cancelada',
}


def _estilos():

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='TituloApp',
        fontSize=20,
        textColor=AZUL,
        fontName='Helvetica-Bold',
    ))

    styles.add(ParagraphStyle(
        name='Subtitulo',
        fontSize=10,
        textColor=GRIS,
    ))

    styles.add(ParagraphStyle(
        name='SeccionTitulo',
        fontSize=13,
        textColor=AZUL,
        fontName='Helvetica-Bold',
        spaceBefore=16,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name='TextoNormal',
        fontSize=10,
        textColor=colors.HexColor('#1f2937'),
    ))

    styles.add(ParagraphStyle(
        name='SinDatos',
        fontSize=10,
        textColor=GRIS,
        fontName='Helvetica-Oblique',
    ))

    return styles


def _fecha_local(valor, formato):
    """Formatea una fecha y hora guardada en UTC en la hora local (TIME_ZONE)."""
    return timezone.localtime(valor).strftime(formato)


def _estado_tratamiento(medicamento):

    hoy = timezone.localdate()

    if medicamento.fecha_fin and medicamento.fecha_fin < hoy:
        return 'Finalizado'

    tiene_historial = MedicationHistory.objects.filter(
        medication_id=medicamento.id
    ).exists()

    if tiene_historial:
        return 'En curso'

    return 'Pendiente de iniciar'


def _dias_restantes(medicamento):

    if not medicamento.fecha_fin:
        return '—'

    dias = (medicamento.fecha_fin - timezone.localdate()).days

    if dias < 0:
        return 'Finalizado'

    if dias == 0:
        return 'Termina hoy'

    return f'{dias} día(s)'


def _tabla_estilo_base():

    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ])


def generar_pdf_paciente(patient, cuidador):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
    )

    styles = _estilos()

    story = []

    # =====================================
    # ENCABEZADO
    # =====================================

    if os.path.exists(LOGO_PATH):

        logo = Image(LOGO_PATH, width=3.2 * cm, height=2.27 * cm)

        encabezado = Table(
            [[logo, Paragraph('MedAlert<br/><font size=10 color="#6b7280">Reporte de paciente</font>', styles['TituloApp'])]],
            colWidths=[3.6 * cm, 13 * cm],
        )

        encabezado.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(encabezado)

    else:

        story.append(Paragraph('MedAlert — Reporte de paciente', styles['TituloApp']))

    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        f'Generado el {timezone.localdate().strftime("%d/%m/%Y")}',
        styles['Subtitulo']
    ))

    story.append(Spacer(1, 0.6 * cm))

    # =====================================
    # DATOS DEL CUIDADOR
    # =====================================

    story.append(Paragraph('Cuidador responsable', styles['SeccionTitulo']))

    nombre_cuidador = f'{cuidador.first_name} {cuidador.last_name}'.strip() or cuidador.username

    identificacion_cuidador = '—'
    genero_cuidador = '—'

    if hasattr(cuidador, 'caregiver_profile'):

        identificacion_cuidador = cuidador.caregiver_profile.identificacion
        genero_cuidador = GENERO_LEGIBLE.get(
            cuidador.caregiver_profile.genero,
            cuidador.caregiver_profile.genero
        )

    story.append(Table(
        [
            ['Nombre:', nombre_cuidador, 'Identificación:', identificacion_cuidador],
            ['Correo:', cuidador.email or '—', 'Género:', genero_cuidador],
        ],
        colWidths=[3 * cm, 6 * cm, 3 * cm, 5 * cm],
        style=TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ])
    ))

    # =====================================
    # DATOS DEL PACIENTE
    # =====================================

    story.append(Paragraph('Datos del paciente', styles['SeccionTitulo']))

    story.append(Table(
        [
            ['Nombre:', f'{patient.nombres} {patient.apellidos}', 'Identificación:', patient.identificacion],
            ['Género:', GENERO_LEGIBLE.get(patient.genero, patient.genero), 'Registrado el:', _fecha_local(patient.created_at, '%d/%m/%Y')],
        ],
        colWidths=[3 * cm, 6 * cm, 3 * cm, 5 * cm],
        style=TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ])
    ))

    # =====================================
    # MEDICAMENTOS
    # =====================================

    story.append(Paragraph('Medicamentos', styles['SeccionTitulo']))

    medicamentos = patient.medications.all().order_by('-created_at')

    if medicamentos:

        filas = [['Medicamento', 'Dosis', 'Frecuencia', 'Estado', 'Restante']]

        for med in medicamentos:

            filas.append([
                med.nombre,
                med.dosis,
                med.frecuencia,
                _estado_tratamiento(med),
                _dias_restantes(med),
            ])

        tabla = Table(
            filas,
            colWidths=[4 * cm, 2.5 * cm, 3.5 * cm, 3.5 * cm, 3 * cm],
            repeatRows=1,
        )

        tabla.setStyle(_tabla_estilo_base())

        story.append(tabla)

    else:

        story.append(Paragraph('No hay medicamentos registrados.', styles['SinDatos']))

    # =====================================
    # HISTORIAL DE TOMAS
    # =====================================

    story.append(Paragraph('Historial de tomas recientes', styles['SeccionTitulo']))

    historial = MedicationHistory.objects.filter(
        patient=patient
    ).select_related('medication').order_by('-tomado_en')[:20]

    if historial:

        filas = [['Medicamento', 'Tomado el']]

        for item in historial:

            filas.append([
                item.medication.nombre,
                _fecha_local(item.tomado_en, '%d/%m/%Y %H:%M'),
            ])

        tabla = Table(
            filas,
            colWidths=[8 * cm, 8.5 * cm],
            repeatRows=1,
        )

        tabla.setStyle(_tabla_estilo_base())

        story.append(tabla)

    else:

        story.append(Paragraph('No hay tomas registradas todavía.', styles['SinDatos']))

    # =====================================
    # CITAS MÉDICAS (agrupadas por tipo)
    # =====================================

    story.append(Paragraph('Citas médicas', styles['SeccionTitulo']))

    citas = patient.appointments.all().order_by('fecha', 'hora')

    if citas:

        for tipo_key, tipo_label in TIPO_CITA_LEGIBLE.items():

            citas_del_tipo = [c for c in citas if c.tipo == tipo_key]

            if not citas_del_tipo:
                continue

            story.append(Paragraph(tipo_label, styles['TextoNormal']))
            story.append(Spacer(1, 0.15 * cm))

            filas = [['Fecha', 'Hora', 'Doctor', 'Especialidad', 'Lugar', 'Estado']]

            for cita in citas_del_tipo:

                filas.append([
                    cita.fecha.strftime('%d/%m/%Y'),
                    cita.hora.strftime('%H:%M'),
                    cita.doctor,
                    cita.especialidad,
                    cita.lugar,
                    ESTADO_CITA_LEGIBLE.get(cita.estado, cita.estado),
                ])

            tabla = Table(
                filas,
                colWidths=[2.3 * cm, 1.8 * cm, 3.2 * cm, 3.2 * cm, 3.5 * cm, 2.5 * cm],
                repeatRows=1,
            )

            tabla.setStyle(_tabla_estilo_base())

            story.append(tabla)
            story.append(Spacer(1, 0.4 * cm))

    else:

        story.append(Paragraph('No hay citas médicas registradas.', styles['SinDatos']))

    doc.build(story)

    buffer.seek(0)

    return buffer
