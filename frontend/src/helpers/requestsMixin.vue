<script>
import axios from 'axios';
import { apiPath } from '../config'

export default {
    computed:{
        langHeader() {
            return { 'Accept-Language': this.$root.$i18n.locale };
        }
    }, 
    methods:{
        request(method, url, options={}) {
            return axios({
                method: method,
                url: apiPath + url,
                params: options.params,
                headers: { ...options.headers, ...this.authHeader, ...this.langHeader },
                data: options.data
            }).catch(error => { this.manageError(error); throw error; })
        },
        manageError(error) {
            if (error.response) {
                /*
                 * The request was made and the server responded with a
                 * status code that falls out of the range of 2xx
                 */
                if (error.response.status == 400) {
                    // Client bad request
                    this.$store.dispatch('alert/error', error.response.data.toString());
                } else {
                    // Other errors
                    console.log(error.response.data);
                    console.log(error.response.status);
                    console.log(error.response.headers);
                    this.$store.dispatch('alert/error', this.$t("Server Response {code} at {url}", { code: error.response.status, url: error.request.responseURL }));
                }
            } else if (error.request) {
                /*
                 * The request was made but no response was received, `error.request`
                 * is an instance of XMLHttpRequest in the browser and an instance
                 * of http.ClientRequest in Node.js
                 */
                console.log(error.request);
                this.$store.dispatch('alert/error', this.$t("Server did not respond"));
            } else {
                // Something happened in setting up the request and triggered an Error
                console.error(error.message);                
                this.$store.dispatch('alert/error', this.$t("App Error: {error}", { error: error.message }));
            }
        },
    }
};
</script>