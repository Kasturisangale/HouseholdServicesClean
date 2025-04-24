import { createRouter, createWebHistory } from 'vue-router';
// import { jwtDecode } from 'jwt-decode';  // Corrected import statement
import HomePage from './views/HomePage.vue';
import AdminLogin from './views/AdminLogin.vue';
import CustomerLogin from './views/CustomerLogin.vue';
import ProfessionalLogin from './views/ProfessionalLogin.vue';
import CustomerRegister from './views/CustomerRegister.vue';
import ProfessionalRegister from './views/ProfessionalRegister.vue';
import AdminDashboard from './views/AdminDashboard.vue';
import CustomerDashboard from './views/CustomerDashboard.vue';
import ProfessionalDashboard from './views/ProfessionalDashboard.vue';
import AdminCustomerInfo from './views/AdminCustomerInfo.vue';
import AdminServiceInfo from './views/AdminServiceInfo.vue';
import UserBlocked from './views/UserBlocked.vue';
import AdminServiceRequestInfo from './views/AdminServiceRequestInfo.vue';
import AdminProfessionalInfo from './views/AdminProfessionalInfo.vue';

import NotFound from './views/NotFound.vue'; 

const routes = [
    { path: '/', component: HomePage, meta: { title: 'Home' } },
    { path: '/adminlogin', component: AdminLogin, meta: { title: 'Admin Login' } },
    { path: '/admin', redirect: '/adminlogin' }, 
    { path: '/customerlogin', component: CustomerLogin, meta: { title: 'Customer Login' } },
    { path: '/professionallogin', component: ProfessionalLogin, meta: { title: 'Professional Login' } },
    { path: '/customerregister', component: CustomerRegister, meta: { title: 'Customer Register' } },
    { path: '/professionalregister', component: ProfessionalRegister, meta: { title: 'Professional Register' } },
    { path: '/admin/dashboard', component: AdminDashboard, meta: { title: 'Admin Dashboard', requiresAuth: true } },
    { path: '/customer/dashboard', component: CustomerDashboard, meta: { title: 'Customer Dashboard', requiresAuth: true } },
    { path: '/professional/dashboard', component: ProfessionalDashboard, meta: { title: 'Professional Dashboard', requiresAuth: true } },
    { path: '/admin/customerinfo', component: AdminCustomerInfo, meta: { title: 'Admin Customer Info' } },
    { path: '/blocked', component: UserBlocked, meta: { title: 'User Blocked' } },
    { path: '/admin/servicerequestinfo', component: AdminServiceRequestInfo, meta: { title: 'Admin Service Request Info' } },
    { path: '/admin/serviceinfo', component: AdminServiceInfo, meta: { title: 'Admin Service Info' } },

    { path: '/admin/professionalinfo', component: AdminProfessionalInfo, meta: { title: 'Admin Professional Info' } },

    { path: '/:catchAll(.*)', component: NotFound }, 
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// router.beforeEach((to, from, next) => {
//     document.title = to.meta.title || 'Default Title';

//     const token = localStorage.getItem('token');
//     if (to.meta.requiresAuth) {
//         if (token) {
//             try {
//                 const decoded = jwtDecode(token); 
//                 if (decoded.exp * 1000 < Date.now()) {
//                     alert('Session expired. Please log in again.');
//                     localStorage.removeItem('token');
//                     return next('/customerlogin');
//                 }
//                 return next(); 
//             } catch (error) {
//                 console.error('Invalid token:', error);
//                 localStorage.removeItem('token');
//                 return next('/customerlogin'); 
//             }
//         } else {
//             alert('You need to log in to access this page.');
//             return next('/customerlogin');
//         }
//     }

//     if (token && (to.path === '/customerlogin' || to.path === '/customerregister')) {
//         return next('/'); 
//     }

//     next();
// });

export default router; 