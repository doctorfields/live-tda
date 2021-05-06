export const alert = {
    namespaced: true,
    state: {
        type: null,
        message: null,
        active: false
    },
    actions: {
        info({ commit }, message) {
            commit('info', message);
        },
        success({ commit }, message) {
            commit('success', message);
        },
        error({ commit }, message) {
            commit('error', message);
        },
        warning({ commit }, message) {
            commit('warning', message);
        },
        clear({ commit }, message) {
            commit('clear', message);
        }
    },
    mutations: {
        info(state, message) {
            state.type = 'info';
            state.message = message;
            state.active = true;
        },
        success(state, message) {
            state.type = 'success';
            state.message = message;
            state.active = true;
        },
        error(state, message) {
            state.type = 'error';
            state.message = message;
            state.active = true;
        },
        warning(state, message) {
            state.type = 'warning';
            state.message = message;
            state.active = true;
        },
        clear(state) {
            state.type = null;
            state.message = null;
            state.active = false;
        }
    }
}
