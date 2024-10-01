<template>
    <div class="category-price-wrapper">
        <h2>{{ categoryName }}</h2>
        <div v-if="isLoading" class="loading">Loading...</div>
        <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
        <table v-if="!isLoading && !errorMessage">
            <thead>
                <tr>
                    <th>商品名稱</th>
                    <th>規格</th>
                    <th>{{latestDataTime}} 最新價格</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="data in priceData" :key="data.編號">
                    <td>{{ data.產品名稱 }}</td>
                    <td>{{ data.規格 }}</td>
                    <td>{{ latestPrice(data.統計值) }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
import Categories from '@/constants/categories';

export default {
    props: {
        category: {
            type: String,
            required: true
        },
        priceData: {
            type: Array,
            required: true
        },
        isLoading: {
            type: Boolean,
            required: true
        },
        errorMessage: {
            type: String,
            required: false
        },
    },
    computed: {
        categoryName() {
            return Categories[this.category];
        },
        latestDataTime(){
            let timeTmp = this.priceData[0].時間終點.split('-');
            return timeTmp[0] + '.' + timeTmp[1];
        }
    },
    methods: {
        latestPrice(prices_str) {
            let number = prices_str.split(',').map(Number);
            let i = number.length - 1;
            while (i >= 0 && number[i] == 0) {
                i--;
            }
            return i == -1 ? "-" : number[i];
        }
    }
};
</script>

<style scoped>
.category-price-wrapper {
    background-color: #f9fafc;
    border-radius: 10px;
    padding: 1.5em;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease-in-out;
    max-width: 1000px;
    min-width: 45vw;
    margin: 0 auto;
    font-family: 'Helvetica Neue', sans-serif;
}

h2 {
    font-size: 1.8em;
    font-weight: 700;
    margin-bottom: 1em;
    color: black;
    text-align: center;
}

.loading {
    text-align: center;
    font-size: 1.2em;
    color: #999;
}

.error {
    color: #e74c3c;
    text-align: center;
    font-size: 1.2em;
}

table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
    overflow: hidden;
    border-radius: 10px;
}

th, td {
    border: 1px solid #ddd;
    padding: 1em;
    font-size: 1em;
    color: #333;
    text-align: center;
}

th {
    background-color: #355f81;
    color: white;
    font-weight: 600;
}

tr {
    background-color: #f8f9fa;
}

tr:nth-child(odd) {
    background-color: #f1f3f5;
}

@media (max-width: 768px) {
    .category-price-wrapper {
        padding: 1em;
        border-radius: 0px;
    }

    h2 {
        font-size: 1.5em;
    }

    th, td {
        padding: 0.75em;
        font-size: 0.9em;
    }
}
</style>