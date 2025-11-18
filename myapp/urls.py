from django.urls import path
from .views import (
    dashboard_view, uji_saring_view, welcome_page, petugas as petugas_view, 
    pendonor, daftar_pendonor_view, riwayat_gagal_donor_view, 
    pendonor_form_view, edit_pendonor_view, kuesioner_view, 
    delete_petugas, edit_petugas, delete_pendonor, 
    verifikasi_lanjut_view, save_verifikasi_lanjut_data, save_final_verifikasi, 
    get_donor_history, generate_donor_pdf, save_aftap_data, panggil_pendonor_view, 
    tambah_pendonor_lama_view
)

app_name = 'myapp'

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('uji-saring/', uji_saring_view, name='uji_saring'),
    path('welcome/', welcome_page, name='welcome'),
    path('petugas/', petugas_view, name='petugas'),
    path('pendonor/', pendonor, name='pendonor'),
    path('daftar-pendonor/', daftar_pendonor_view, name='daftar_pendonor'),
    path('riwayat-gagal-donor/', riwayat_gagal_donor_view, name='riwayat_gagal_donor'),
    path('pendonor/add/', pendonor_form_view, name='add_pendonor'),
    path('pendonor/edit/<int:pk>/', edit_pendonor_view, name='edit_pendonor'),
    path('kuesioner/<int:pendonor_id>/', kuesioner_view, name='kuesioner'),
    path('petugas/delete/', delete_petugas, name='delete_petugas'),
    path('petugas/edit/', edit_petugas, name='edit_petugas'),
    path('pendonor/delete/<int:pk>/', delete_pendonor, name='delete_pendonor'),
    path('verifikasi-lanjut/<int:verifikasi_id>/', verifikasi_lanjut_view, name='verifikasi_lanjut'),
    path('save-verifikasi-lanjut/<int:pendonor_id>/', save_verifikasi_lanjut_data, name='save_verifikasi_lanjut'),
    path('save-final-verifikasi/<int:pendonor_id>/', save_final_verifikasi, name='save_final_verifikasi'),
    path('get-donor-history/<str:nik_ktp>/', get_donor_history, name='get_donor_history'),
    path('generate-pdf/<int:verifikasi_id>/', generate_donor_pdf, name='generate_donor_pdf'),
    path('save-aftap-data/<int:verifikasi_id>/', save_aftap_data, name='save_aftap_data'),
    path('panggil-pendonor/', panggil_pendonor_view, name='panggil_pendonor'),
    path('tambah-pendonor-lama/', tambah_pendonor_lama_view, name='tambah_pendonor_lama'),
]