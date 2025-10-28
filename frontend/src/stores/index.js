import { createPinia } from "pinia";
import persist from 'pinia-plugin-persistedstate'

// 创建 Pinia 实例
const pinia = createPinia()
pinia.use(persist)

export default pinia

export * from './user'