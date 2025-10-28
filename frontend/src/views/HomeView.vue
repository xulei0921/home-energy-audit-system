<template>
    <div class="home-view">
        <el-row :gutter="20">
            <el-col :span="16">
                <EnergyDashboard />
            </el-col>
            <el-col :span="8">
                <el-card class="recommendations-sidebar">
                    <template #header>
                        <div class="sidebar-header">
                            <h3>节能建议</h3>
                            <el-button type="primary" text >
                                生成新建议
                            </el-button>
                        </div>
                    </template>

                    <div class="recommendations-list">
                        建议列表
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup>
import EnergyDashboard from '@/components/EnergyDashboard.vue';
</script>

<style scoped>

</style>