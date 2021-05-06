<template>
    <v-menu offset-y>
        <template v-slot:activator="{ on }">
            <v-btn text v-on="on">{{ $i18n.locale }}</v-btn>
        </template>
        <v-list>
            <v-list-item
                v-for="(item, index) in languages"
                :key="index"
                @click="changeLocale(index)"
                dense
            >
                <v-list-item-title>{{ item.name }}</v-list-item-title>
            </v-list-item>
        </v-list>
    </v-menu>
</template>

<script>
export default {
    data() {
        return {
            languages: [
                { locale: 'ca', name: 'Català' },
                { locale: 'es', name: 'Español' },
                { locale: 'en', name: 'English' },
            ]
        }
    },
    methods: {
        changeLocale(index) {
            this.$root.$i18n.locale=this.languages[index].locale
        }
    }
}
</script>

<style scoped></style>
