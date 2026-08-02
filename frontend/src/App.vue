<script setup>
import { Toaster } from 'vue-sonner'
</script>

<template>

  <RouterView />

  <Toaster
    richColors
    position="top-right"
  />

</template>