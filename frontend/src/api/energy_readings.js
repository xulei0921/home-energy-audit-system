import request from '@/utils/request'

// 获取能耗分析
export const getEnergyAnalysis = () => {
    return request.get('/energy-readings/analysis')
}