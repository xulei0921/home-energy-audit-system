import axios from "axios";
import router from "@/router";
import { useUserStore } from "@/stores";

const baseURL = '/api'

const instance = axios.create({
    baseURL,
    timeout: 5000
})

// 请求拦截器
instance.interceptors.request.use(
    (config) => {
        // 携带token
        const userStore = useUserStore()
        if (useUserStore.token) {
            config.headers.Authorization = `Bearer ${userStore.token}`
        }
        return config
    },
    (err) => Promise.reject(err)
)

// 响应拦截器
instance.interceptors.response.use(
    (res) => {
        return res.data
    },
    (err) => {
        // 处理401错误，权限不足 或 token过期 => 拦截到登录
        if (err.response?.status === 401) {
            const userStore = useUserStore()
            if (userStore.token) {
                userStore.removeToken()
            }
            router.push('/login')
            ElMessage.error({ message: err.response?.data?.detail } || '请求失败，请稍后重视')
            return Promise.reject(err.response?.data?.detail || '请求失败')
        }

        // 错误的默认情况 => 只要给提示
        const errorMsg = err.response?.data?.detail || '请求失败，请稍后重试'
        ElMessage.error(errorMsg)
        return Promise.reject(errorMsg)
    }
)

export default instance
export { baseURL }