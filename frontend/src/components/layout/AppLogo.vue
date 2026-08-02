<template>

  <svg
    viewBox="0 0 100 100"
    class="w-full h-full"
  >

    <g transform="translate(50,54) rotate(-25)">

      <path
        :class="animated ? 'medalert-pill-left' : ''"
        d="M0,-12 L-16,-12 A12,12 0 0,0 -16,12 L0,12 Z"
        fill="#1d4ed8"
      />

      <path
        :class="animated ? 'medalert-pill-right' : ''"
        d="M0,-12 L16,-12 A12,12 0 0,1 16,12 L0,12 Z"
        fill="#fb923c"
      />

      <line
        v-if="!animated"
        x1="0"
        y1="-12"
        x2="0"
        y2="12"
        stroke="white"
        stroke-width="1.2"
        opacity="0.6"
      />

    </g>

    <circle
      v-if="animated"
      class="medalert-ping"
      cx="74"
      cy="26"
      r="4.3"
      fill="none"
      stroke="#fb923c"
      stroke-width="1.6"
    />

    <circle
      cx="74"
      cy="26"
      r="7"
      fill="none"
      stroke="#fb923c"
      stroke-width="1.6"
      opacity="0.35"
    />

    <circle
      cx="74"
      cy="26"
      r="4.3"
      fill="none"
      stroke="#fb923c"
      stroke-width="1.6"
      opacity="0.6"
    />

    <circle
      cx="74"
      cy="26"
      r="2"
      fill="#fb923c"
    />

  </svg>

</template>

<script setup lang="ts">
defineProps({

  animated: {
    type: Boolean,
    default: false,
  },

})
</script>

<style scoped>
.medalert-pill-left {
  animation: medalert-open-left 2.6s ease-in-out infinite;
}

.medalert-pill-right {
  animation: medalert-open-right 2.6s ease-in-out infinite;
}

.medalert-ping {
  transform-origin: 74px 26px;
  animation: medalert-radar 1.8s ease-out infinite;
}

@keyframes medalert-open-left {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(-4px); }
}

@keyframes medalert-open-right {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(4px); }
}

@keyframes medalert-radar {
  0% { transform: scale(1); opacity: 0.7; }
  100% { transform: scale(2.6); opacity: 0; }
}
</style>
