<template>
    <div class="energy-dashboard">
        <el-row :gutter="20">
            <!-- 关键指标 -->
            <el-col :span="6">
                <el-card class="metric-card">
                    <template #header>
                        <div class="card-header">
                            <span>本月总能耗</span>
                        </div>
                    </template>
                    <div class="metric-value"></div>
                    <div class="metric-trend">

                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { getEnergyAnalysis } from '@/api/energy_readings';

const analysis = ref({})

const fetchEnergyAnalysis = async () => {
    try {
        const data = await getEnergyAnalysis()
        analysis.value = data
        console.log(analysis.value)
    } catch (error) {
        console.error(error)
    }
}

onMounted(() => {
    fetchEnergyAnalysis()
})
</script>

<style scoped>

</style>