
<template>
  <div class="about-container container">
    <div class="about-header">
        <h1>About LivingSpace</h1>
        <p class="subtitle">Designing homes, building dreams.</p>
    </div>

    <el-row :gutter="40" class="about-section">
        <el-col :md="12">
            <el-image src="https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" class="about-image" />
        </el-col>
        <el-col :md="12" class="about-text">
            <h2>Our Story</h2>
            <p>
                Founded in 2026, LivingSpace began with a simple mission: to make high-quality, stylish furniture accessible to everyone. We believe that your home should be a reflection of your personality and a sanctuary of comfort.
            </p>
            <p>
                Our curated collection features pieces from artisans around the world, blending modern aesthetics with timeless durability. Whether you are furnishing a cozy apartment or a spacious family home, we have something for every corner of your life.
            </p>
        </el-col>
    </el-row>

    <div class="values-section">
        <h2 style="text-align: center; margin-bottom: 40px;">Why Choose Us</h2>
        <el-row :gutter="30">
            <el-col :sm="8" class="value-card">
                <el-icon :size="40" color="#8B5E3C"><Medal /></el-icon>
                <h3>Quality Craftsmanship</h3>
                <p>We partner with skilled manufacturers who use only the finest materials.</p>
            </el-col>
            <el-col :sm="8" class="value-card">
                <el-icon :size="40" color="#8B5E3C"><Van /></el-icon>
                <h3>Fast Shipping</h3>
                <p>Get your furniture delivered safely and quickly to your doorstep.</p>
            </el-col>
            <el-col :sm="8" class="value-card">
                <el-icon :size="40" color="#8B5E3C"><Service /></el-icon>
                <h3>24/7 Support</h3>
                <p>Our dedicated team is always here to assist you with your needs.</p>
            </el-col>
        </el-row>
    </div>
  </div>
</template>

<script setup>
import { Medal, Van, Service } from '@element-plus/icons-vue'
</script>

<style scoped>
.about-container {
    padding: 80px 20px;
}

.about-header {
    text-align: center;
    margin-bottom: 80px;
}

.about-header h1 {
    font-size: 3.5rem;
    margin-bottom: 16px;
    font-family: var(--font-serif);
    color: var(--color-secondary);
}

.subtitle {
    font-size: 1.3rem;
    color: var(--color-primary);
    font-style: italic;
    font-family: var(--font-serif);
}

.about-section {
    margin-bottom: 100px;
    align-items: center;
}

.about-image {
    width: 100%;
    border-radius: 12px;
    box-shadow: var(--shadow-hover);
    transition: transform 0.3s ease;
}

.about-image:hover {
    transform: scale(1.02);
}

.about-text h2 {
    font-size: 2rem;
    margin-bottom: 24px;
    color: var(--color-accent);
    font-family: var(--font-serif);
}

.about-text p {
    font-size: 1.1rem;
    line-height: 1.7;
    color: var(--color-text-main);
    margin-bottom: 24px;
}

.values-section h2 {
    text-align: center;
    margin-bottom: 60px;
    font-family: var(--font-serif);
    font-size: 2.5rem;
}

.value-card {
    text-align: center;
    padding: 40px 20px;
    background: var(--color-white);
    border-radius: 12px;
    box-shadow: var(--shadow-card);
    transition: all 0.3s ease;
    margin-bottom: 20px;
}

.value-card:hover {
    transform: translateY(-10px);
    box-shadow: var(--shadow-hover);
}

.value-card h3 {
    margin: 20px 0 12px;
    font-family: var(--font-serif);
    color: var(--color-secondary);
}

.value-card p {
    color: var(--color-text-light);
}
</style>
