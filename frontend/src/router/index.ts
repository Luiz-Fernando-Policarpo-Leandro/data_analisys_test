import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import OperadorasList from '../views/OperadorasList.vue'
import OperadoraDetalhe from '../views/OperadoraDetalhe.vue'
import Estatisticas from '../views/Estatisticas.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', component: OperadorasList },
  { 
    path: '/operadoras/:cnpj', 
    name: 'operadora-detalhe',
    component: OperadoraDetalhe, 
    props: true 
  },
  { path: '/estatisticas', component: Estatisticas }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

