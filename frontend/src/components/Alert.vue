<template>
    <v-snackbar
        v-model="alert.active"
        :color="alertColor"
        :timeout="timeout"
        :top="true">        
        <v-icon class="mx-3" dark>{{ alertIcon }}</v-icon>
        <span>{{ alert.message }}</span>
        <v-btn dark icon @click="alert.active = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
    </v-snackbar>
</template>

<script>
import { mapState } from 'vuex'

export default {
  data () {
    return {
      timeout: 6000
    }
  },
  computed: {
    ...mapState([
      'alert'
    ]),
    alertColor(state) {
      switch(state.alert.type) {
        case 'info':    return 'dark';
        case 'success': return 'success';
        case 'warning': return 'warning';
        case 'error':   return 'error';
        default:        return 'dark';
      }
    },
    alertIcon(state) {
      switch(state.alert.type) {
        case 'info':    return 'mdi-information';
        case 'success': return 'mdi-check-circle';
        case 'warning': return 'mdi-alert-outline';
        case 'error':   return 'mdi-alert-circle';
        default:        return 'mdi-information';
      }
    },
  }
}
</script>
