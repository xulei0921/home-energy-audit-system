import { defineStore } from "pinia";
import { ref } from "vue";
import { isTokenExpired } from "@/utils/jwt";

// 用户模块 token setToken removeToken
export const useUserStore = defineStore('user', () => {
    const token = ref('')

    const setToken = (newToken) => {
        token.value = newToken
    }
    const removeToken = () => {
        token.value = ''
    }

    const isLogin = () => {
        if (isTokenExpired(token.value)) {
            token.value = ''
            return false
        }
        return true
    }

    return {
        token,
        setToken,
        removeToken,
        isLogin
    }
}, {
    persist: true
})