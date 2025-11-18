import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from zoneinfo import ZoneInfo
import datetime
from django.utils import timezone
from datetime import timedelta
from django.db.models import Subquery, OuterRef, Max, F, Q, Count

from django.conf import settings
import os

from .models import Petugas, Pendonor, Verifikasi
from .forms import PetugasForm, PendonorForm, KuesionerForm, VerifikasiForm, VerifikasiLanjutForm, FullPendonorVerifikasiForm

def welcome_page(request):
    blood_group_stats = {}
    for blood_group_choice, _ in Pendonor.GOLONGAN_DARAH_CHOICES:
        total_count = Pendonor.objects.filter(golongan_darah=blood_group_choice).count()
        male_count = Pendonor.objects.filter(golongan_darah=blood_group_choice, jenis_kelamin='Laki-laki').count()
        female_count = Pendonor.objects.filter(golongan_darah=blood_group_choice, jenis_kelamin='Perempuan').count()
        
        blood_group_stats[blood_group_choice] = {
            'total': total_count,
            'Laki_laki': male_count,
            'Perempuan': female_count,
        }
    
    context = {
        'blood_group_stats': blood_group_stats,
    }
    return render(request, 'welcome.html', context)

def dashboard_view(request):
    return welcome_page(request)

def uji_saring_view(request):
    return render(request, 'uji_saring.html')

def pendonor_form_view(request):
    if request.method == 'POST':
        form = PendonorForm(request.POST)
        if form.is_valid():
            pendonor = form.save()
            return redirect('myapp:kuesioner', pendonor_id=pendonor.id)
    else:
        form = PendonorForm()
    return render(request, 'pendonor_form.html', {'form': form})

def edit_pendonor_view(request, pk):
    pendonor_instance = get_object_or_404(Pendonor, pk=pk)
    if request.method == 'POST':
        form = PendonorForm(request.POST, instance=pendonor_instance)
        if form.is_valid():
            pendonor = form.save()
            return redirect('myapp:kuesioner', pendonor_id=pendonor.id)
    else:
        form = PendonorForm(instance=pendonor_instance)
    return render(request, 'pendonor_form.html', {'form': form})

def kuesioner_view(request, pendonor_id):
    pendonor = get_object_or_404(Pendonor, id=pendonor_id)
    verifikasi, created = Verifikasi.objects.get_or_create(pendonor=pendonor)

    if request.method == 'POST':
        form = KuesionerForm(request.POST, instance=verifikasi)
        if form.is_valid():
            verifikasi = form.save(commit=False) # Save form data to instance, but don't commit yet

            alasan = []
            if form.cleaned_data['q1_sehat_hari_ini'] == 'Tidak':
                alasan.append('Pendonor sedang tidak sehat.')
            if form.cleaned_data['q2_minum_obat'] == 'Iya':
                alasan.append('Sedang minum obat penghilang nyeri.')
            if form.cleaned_data['q3a_diabetes'] == 'Iya':
                alasan.append('Riwayat Diabetes.')
            if form.cleaned_data['q3b_ginjal'] == 'Iya':
                alasan.append('Riwayat Ginjal.')
            if form.cleaned_data['q3c_gangguan_darah'] == 'Iya':
                alasan.append('Riwayat Gangguan darah.')
            if form.cleaned_data['q3d_malaria'] == 'Iya':
                alasan.append('Riwayat Malaria.')
            if form.cleaned_data['q3e_ashma'] == 'Iya':
                alasan.append('Riwayat Ashma/sesak nafas.')
            if form.cleaned_data['q3f_alergi'] == 'Iya':
                alasan.append('Riwayat Alergi.')
            if form.cleaned_data['q3g_tbc'] == 'Iya':
                alasan.append('Riwayat TBC.')
            if form.cleaned_data['q3h_hepatitis'] == 'Iya':
                alasan.append('Riwayat Hepatitis/Sakit Kuning.')
            if form.cleaned_data['q3i_jantung'] == 'Iya':
                alasan.append('Riwayat Jantung.')
            if form.cleaned_data['q4_pingsan_kejang'] == 'Iya':
                alasan.append('Sering pingsan/kejang-kejang.')
            if form.cleaned_data['q5_gejala_hiv'] == 'Iya':
                alasan.append('Mempunyai gejala kemungkinan pengidap HIV.')
            if form.cleaned_data['q6_tindik_tato'] == 'Iya':
                alasan.append('Melakukan tindik telinga/tato dalam 6 bulan terakhir.')
            if form.cleaned_data['q7_keluar_daerah'] == 'Iya':
                alasan.append('Pernah keluar daerah dalam 3 bulan terakhir.')
            if form.cleaned_data['q8_cabut_gigi'] == 'Iya':
                alasan.append('Dalam 3 minggu terakhir cabut gigi.')
            if form.cleaned_data['q9_identitas_lain'] == 'Iya':
                alasan.append('Pernah menyumbangkan darah dengan memakai identitas lain.')
            if form.cleaned_data['q10_donor_kurang_3_bulan'] == 'Iya':
                alasan.append('Pernah menyumbangkan darah dalam waktu kurang dari 3 bulan.')
            if form.cleaned_data['q11_wanita_kondisi'] == 'Iya':
                alasan.append('Dalam kondisi hamil/menyusui/haid/habis melahirkan.')

            verifikasi.alasan_tidak_layak = '\n'.join(alasan) if alasan else None
            verifikasi.save() # Now commit the instance with updated alasan_tidak_layak

            # Redirect to the next step, passing the verifikasi_id
            return redirect('myapp:pendonor')
    else:
        form = KuesionerForm(instance=verifikasi)
    return render(request, 'kuesioner.html', {'form': form, 'pendonor': pendonor, 'verifikasi_id': verifikasi.id})

def verifikasi_lanjut_view(request, verifikasi_id):
    verifikasi = get_object_or_404(Verifikasi, id=verifikasi_id)
    pendonor = verifikasi.pendonor # Get pendonor from verifikasi_instance

    if request.method == 'POST':
        form = VerifikasiLanjutForm(request.POST, instance=verifikasi)
        if form.is_valid():
            form.save()
            return redirect('myapp:pendonor')
    else:
        form = VerifikasiLanjutForm(instance=verifikasi)
    return render(request, 'verifikasi_lanjut.html', {'form': form, 'pendonor': pendonor})

def pendonor(request):
    all_pendonor = Pendonor.objects.filter(Q(verifikasi__is_verified=False) | Q(verifikasi__isnull=True))
    # Search functionality
    search_query = request.GET.get('search_query')
    if search_query:
        all_pendonor = all_pendonor.filter(
            Q(nama__icontains=search_query) | Q(golongan_darah__icontains=search_query) | Q(nik_ktp__icontains=search_query)
        )

    # Add is_lama and alasan_tidak_layak attribute to each pendonor object
    for p in all_pendonor:
        latest_verifikasi = p.verifikasi_set.order_by('-timestamp').first()
        p.is_lama = p.tgl_donor_terakhir is not None
        if latest_verifikasi:
            p.alasan_tidak_layak = latest_verifikasi.alasan_tidak_layak
        else:
            p.alasan_tidak_layak = ""
        
        if p.is_lama: # If it's an old donor and tgl_donor_terakhir was filled in the form
            p.display_tgl_donor_terakhir = p.tgl_donor_terakhir.strftime("%d %b %Y")
        else: # If it's a new donor, or tgl_donor_terakhir was not filled in the form
            last_successful_donation = Verifikasi.objects.filter(
                pendonor=p, 
                keputusan_petugas='Lanjut Donor'
            ).order_by('-timestamp').first()

            if last_successful_donation and last_successful_donation.timestamp:
                p.display_tgl_donor_terakhir = last_successful_donation.timestamp.strftime("%d %b %Y")
            else:
                p.display_tgl_donor_terakhir = "-"

    months = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]

    verifikasi_form = VerifikasiForm()
    verifikasi_lanjut_form = VerifikasiLanjutForm()
    all_petugas = Petugas.objects.all()

    context = {
        'all_pendonor': all_pendonor,
        'months': months,
        'pendonor_golongan_darah_choices': Pendonor.GOLONGAN_DARAH_CHOICES,
        'pendonor_rhesus_choices': Pendonor.RHESUS_CHOICES,
        'pendonor_jenis_kelamin_choices': Pendonor.JENIS_KELAMIN_CHOICES,
        'search_query': search_query,
        'verifikasi_form': verifikasi_form,
        'verifikasi_lanjut_form': verifikasi_lanjut_form,
        'all_petugas': all_petugas,
    }
    return render(request, 'pendonor.html', context)

@csrf_exempt
def petugas(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = PetugasForm(data)
            if form.is_valid():
                petugas = form.save()
                return JsonResponse({
                    'success': True,
                    'petugas': {
                        'id': petugas.id,
                        'nama': petugas.nama,
                        'nip': petugas.nip,
                        'jabatan': petugas.jabatan,
                    }
                })
            else:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    all_petugas = Petugas.objects.all()
    context = {
        'all_petugas': all_petugas
    }
    return render(request, 'petugas.html', context)

@csrf_exempt
@require_POST
def delete_petugas(request):
    try:
        data = json.loads(request.body)
        petugas_id = data.get('id')
        petugas = get_object_or_404(Petugas, id=petugas_id)
        petugas.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def edit_petugas(request):
    pass

@csrf_exempt
@require_POST
def delete_pendonor(request, pk):
    try:
        pendonor = get_object_or_404(Pendonor, id=pk)
        pendonor.delete()
        return JsonResponse({'success': True})
    except Http404:
        return JsonResponse({'success': False, 'error': 'Pendonor tidak ditemukan.'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': f'Terjadi kesalahan pada server: {str(e)}'}, status=500)

@csrf_exempt
@require_POST
def save_verifikasi_lanjut_data(request, pendonor_id):
    try:
        pendonor = get_object_or_404(Pendonor, id=pendonor_id)
        verifikasi = Verifikasi.objects.filter(pendonor=pendonor, is_verified=False).order_by('-timestamp').first()
        if not verifikasi:
            verifikasi = Verifikasi.objects.create(pendonor=pendonor)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': {'__all__': ['Invalid JSON format.']}}, status=400)

        form = VerifikasiLanjutForm(data, instance=verifikasi)

        if form.is_valid():
            verifikasi_instance = form.save() # Save the physical exam data

            alasan_fisik_list = []
            physical_exam_details = []

            # Custom validation logic for physical exam
            hb_value = form.cleaned_data.get('hb_value')
            if hb_value is not None:
                hb_reason = None
                if hb_value < 12.5:
                    hb_reason = f'HB Value ({hb_value}) < 12.5'
                    alasan_fisik_list.append(hb_reason)
                elif hb_value > 17:
                    hb_reason = f'HB Value ({hb_value}) > 17'
                    alasan_fisik_list.append(hb_reason)
                physical_exam_details.append({'field': 'HB', 'value': str(hb_value), 'reason': hb_reason if hb_reason else 'Sesuai'})

            tensi = form.cleaned_data.get('tensi')
            if tensi:
                tensi_reason = None
                try:
                    systolic, diastolic = map(int, tensi.split('/'))
                    if systolic < 110 or diastolic < 70:
                        tensi_reason = f'Tensi ({tensi}) < 110/70'
                        alasan_fisik_list.append(tensi_reason)
                    if systolic > 150 or diastolic > 100:
                        tensi_reason = f'Tensi ({tensi}) > 150/100'
                        alasan_fisik_list.append(tensi_reason)
                except (ValueError, TypeError):
                    tensi_reason = f'Format Tensi ({tensi}) tidak valid (contoh: 120/80)'
                    alasan_fisik_list.append(tensi_reason)
                physical_exam_details.append({'field': 'Tensi', 'value': tensi, 'reason': tensi_reason if tensi_reason else 'Sesuai'})

            berat_badan = form.cleaned_data.get('berat_badan')
            if berat_badan is not None:
                bb_reason = None
                if berat_badan < 50:
                    bb_reason = f'Berat Badan ({berat_badan} Kg) < 50 Kg'
                    alasan_fisik_list.append(bb_reason)
                physical_exam_details.append({'field': 'Berat Badan', 'value': str(berat_badan) + ' Kg', 'reason': bb_reason if bb_reason else 'Sesuai'})

            overall_alasan = []
            if verifikasi.alasan_tidak_layak: # Alasan from kuesioner
                overall_alasan.append(verifikasi.alasan_tidak_layak)
            if alasan_fisik_list: # Alasan from physical exam
                overall_alasan.extend(alasan_fisik_list)
            
            is_eligible = not overall_alasan

            verifikasi_instance.save()

            response_data = {
                'success': True,
                'physical_exam_details': physical_exam_details,
                'overall_eligibility': 'Layak' if is_eligible else 'Tidak Layak',
                'all_reasons': '\n'.join(overall_alasan)
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'errors': {'__all__': [f'Terjadi kesalahan pada server: {str(e)}']}}, status=500)



# ... (other views remain unchanged) ...

def daftar_pendonor_view(request):
    # Base query
    base_query = Pendonor.objects.filter(verifikasi__is_verified=True)

    # Search functionality
    search_query = request.GET.get('search_query')
    if search_query:
        base_query = base_query.filter(
            Q(nama__icontains=search_query) | 
            Q(golongan_darah__icontains=search_query) |
            Q(nik_ktp__icontains=search_query)
        )

    # Filter functionality
    golongan_darah = request.GET.get('golongan_darah')
    rhesus = request.GET.get('rhesus')
    tahun = request.GET.get('tahun')
    bulan = request.GET.get('bulan')
    jenis_kelamin = request.GET.get('jenis_kelamin')

    if golongan_darah:
        base_query = base_query.filter(golongan_darah=golongan_darah)
    if rhesus:
        base_query = base_query.filter(rhesus=rhesus)
    if tahun:
        base_query = base_query.filter(verifikasi__timestamp__year=tahun)
    if bulan:
        base_query = base_query.filter(verifikasi__timestamp__month=bulan)
    if jenis_kelamin:
        base_query = base_query.filter(jenis_kelamin=jenis_kelamin)

    # Get the list of unique NIKs from the filtered query
    nik_list = base_query.values_list('nik_ktp', flat=True).distinct()

    # For each NIK, get the most recent Pendonor record that has a verified Verifikasi
    final_pendonor_list = []
    for nik in nik_list:
        # Find the latest pendonor entry for this NIK based on the latest *verified* verification
        latest_pendonor_for_nik = Pendonor.objects.filter(
            nik_ktp=nik, 
            verifikasi__is_verified=True
        ).order_by('-verifikasi__timestamp').first()
        if latest_pendonor_for_nik:
            final_pendonor_list.append(latest_pendonor_for_nik)

    # For each donor, get their latest verification attempt to display
    for p in final_pendonor_list:
        # The latest verifikasi is already implicitly handled by how we selected the donor,
        # but we need to fetch it again to get the details.
        latest_verifikasi = p.verifikasi_set.order_by('-timestamp').first()
        p.is_lama = p.tgl_donor_terakhir is not None
        
        # Use p.tgl_donor_terakhir for display, as requested by the user
        if p.tgl_donor_terakhir:
            p.display_tgl_donor_terakhir = p.tgl_donor_terakhir.strftime("%d %b %Y")
        else:
            p.display_tgl_donor_terakhir = "-"
        
        # Keep alasan_tidak_layak from the latest verification if needed elsewhere
        if latest_verifikasi:
            p.alasan_tidak_layak = latest_verifikasi.alasan_tidak_layak
        else:
            p.alasan_tidak_layak = ""

    months = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]

    context = {
        'all_pendonor': final_pendonor_list,
        'months': months,
        'pendonor_golongan_darah_choices': Pendonor.GOLONGAN_DARAH_CHOICES,
        'pendonor_rhesus_choices': Pendonor.RHESUS_CHOICES,
        'pendonor_jenis_kelamin_choices': Pendonor.JENIS_KELAMIN_CHOICES,
        'selected_golongan_darah': golongan_darah,
        'selected_rhesus': rhesus,
        'selected_tahun': tahun,
        'selected_bulan': bulan,
        'selected_jenis_kelamin': jenis_kelamin,
        'search_query': search_query,
        'all_petugas': Petugas.objects.all(),
    }
    return render(request, 'daftar_pendonor.html', context)

def riwayat_gagal_donor_view(request):
    # Base query on Verifikasi for failed donors
    base_query = Verifikasi.objects.filter(keputusan_petugas='Tidak Lanjut')

    # Search functionality
    search_query = request.GET.get('search_query')
    if search_query:
        base_query = base_query.filter(
            Q(pendonor__nama__icontains=search_query) | 
            Q(pendonor__golongan_darah__icontains=search_query) |
            Q(pendonor__nik_ktp__icontains=search_query)
        )

    # Filter functionality
    golongan_darah = request.GET.get('golongan_darah')
    rhesus = request.GET.get('rhesus')
    tahun = request.GET.get('tahun')
    bulan = request.GET.get('bulan')
    jenis_kelamin = request.GET.get('jenis_kelamin')

    if golongan_darah:
        base_query = base_query.filter(pendonor__golongan_darah=golongan_darah)
    if rhesus:
        base_query = base_query.filter(pendonor__rhesus=rhesus)
    if tahun:
        base_query = base_query.filter(timestamp__year=tahun) # Filter on Verifikasi's timestamp
    if bulan:
        base_query = base_query.filter(timestamp__month=bulan) # Filter on Verifikasi's timestamp
    if jenis_kelamin:
        base_query = base_query.filter(pendonor__jenis_kelamin=jenis_kelamin)

    gagal_verifikasi = base_query.order_by('-timestamp') # Order the final queryset

    jakarta_tz = ZoneInfo("Asia/Jakarta")

    for verifikasi in gagal_verifikasi:
        alasan_kuesioner = verifikasi.alasan_tidak_layak or ''
        
        alasan_fisik_list = []
        if verifikasi.hb_value is not None:
            if verifikasi.hb_value < 12.5:
                alasan_fisik_list.append(f'HB Value ({verifikasi.hb_value}) < 12.5')
            elif verifikasi.hb_value > 17:
                alasan_fisik_list.append(f'HB Value ({verifikasi.hb_value}) > 17')
        if verifikasi.tensi:
            try:
                systolic, diastolic = map(int, verifikasi.tensi.split('/'))
                if systolic < 110 or diastolic < 70:
                    alasan_fisik_list.append(f'Tensi ({verifikasi.tensi}) < 110/70')
                if systolic > 150 or diastolic > 100:
                    alasan_fisik_list.append(f'Tensi ({verifikasi.tensi}) > 150/100')
            except ValueError:
                alasan_fisik_list.append(f'Format Tensi ({verifikasi.tensi}) tidak valid')
        if verifikasi.berat_badan is not None and verifikasi.berat_badan < 50:
            alasan_fisik_list.append(f'Berat Badan ({verifikasi.berat_badan} Kg) < 50 Kg')

        alasan_fisik = '\n'.join(alasan_fisik_list)
        
        verifikasi.alasan_lengkap = f"{alasan_kuesioner}\n{alasan_fisik}".strip()

        if verifikasi.timestamp:
            local_timestamp = verifikasi.timestamp.astimezone(jakarta_tz)
            verifikasi.display_timestamp = local_timestamp.strftime("%d %b %Y %H:%M")
        else:
            verifikasi.display_timestamp = "-"

    months = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember'),
    ]

    context = {
        'gagal_verifikasi': gagal_verifikasi,
        'months': months,
        'pendonor_golongan_darah_choices': Pendonor.GOLONGAN_DARAH_CHOICES,
        'pendonor_rhesus_choices': Pendonor.RHESUS_CHOICES,
        'pendonor_jenis_kelamin_choices': Pendonor.JENIS_KELAMIN_CHOICES,
        'selected_golongan_darah': golongan_darah,
        'selected_rhesus': rhesus,
        'selected_tahun': tahun,
        'selected_bulan': bulan,
        'selected_jenis_kelamin': jenis_kelamin,
        'search_query': search_query,
    }
    return render(request, 'riwayat_gagal_donor.html', context)

@csrf_exempt
@require_POST
def save_final_verifikasi(request, pendonor_id):
    try:
        pendonor = get_object_or_404(Pendonor, id=pendonor_id)
        verifikasi = Verifikasi.objects.filter(pendonor=pendonor, is_verified=False).order_by('-timestamp').first()
        if not verifikasi:
            return JsonResponse({'success': False, 'errors': {'__all__': ['Proses verifikasi tidak ditemukan. Silakan mulai dari awal.']}}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': {'__all__': ['Invalid JSON format.']}}, status=400)

        keputusan_petugas = data.get('keputusan_petugas')
        catatan_dokter = data.get('catatan_dokter')
        petugas_id = data.get('petugas_id')
        overall_eligibility = data.get('overall_eligibility')
        jenis_donasi = data.get('jenis_donasi')
        jenis_donor = data.get('jenis_donor')

        errors = {}
        if keputusan_petugas == 'Lanjut Donor':
            if overall_eligibility == 'Tidak Layak' and not catatan_dokter:
                errors['catatan_dokter'] = 'Catatan dari dokter wajib diisi jika Lanjut Donor dengan status Tidak Layak.'
        
        if not petugas_id:
            errors['petugas'] = 'Petugas wajib dipilih.'

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        verifikasi.keputusan_petugas = keputusan_petugas
        verifikasi.catatan_dokter = catatan_dokter
        verifikasi.is_verified = True
        verifikasi.jenis_donasi = jenis_donasi
        verifikasi.jenis_donor = jenis_donor

        petugas_instance = get_object_or_404(Petugas, id=petugas_id)
        verifikasi.petugas = petugas_instance
        verifikasi.nama_petugas = petugas_instance.nama

        if keputusan_petugas == 'Lanjut Donor':
            pendonor.tgl_donor_terakhir = datetime.date.today()
            pendonor.save()

        verifikasi.save()

        return JsonResponse({'success': True})
    except Exception as e:
        # Log the exception for debugging
        import traceback
        traceback.print_exc()
        # Return a generic error message to the client
        return JsonResponse({'success': False, 'errors': {'__all__': [f'Terjadi kesalahan pada server: {str(e)}']}}, status=500)

@csrf_exempt
@require_POST
def save_aftap_data(request, verifikasi_id):
    try:
        verifikasi = get_object_or_404(Verifikasi, id=verifikasi_id)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': {'__all__': ['Invalid JSON format.']}}, status=400)

        # Extract data from the request
        no_kantong = data.get('no_kantong')
        jenis_kantong = data.get('jenis_kantong')
        pengambilan = data.get('pengambilan')
        stop_cc = data.get('stop_cc')
        diambil_sebanyak = data.get('diambil_sebanyak')
        reaksi_donor = data.get('reaksi_donor')
        petugas_aftap_id = data.get('petugas_aftap_id')

        # Basic validation
        errors = {}
        if not no_kantong:
            errors['no_kantong'] = 'Nomor Kantong wajib diisi.'
        if not jenis_kantong:
            errors['jenis_kantong'] = 'Jenis Kantong wajib dipilih.'
        if not pengambilan:
            errors['pengambilan'] = 'Pengambilan wajib dipilih.'
        if pengambilan == 'Stop' and not stop_cc:
            errors['stop_cc'] = 'Jumlah cc saat dihentikan wajib diisi.'
        if not diambil_sebanyak:
            errors['diambil_sebanyak'] = 'Jumlah diambil wajib dipilih.'
        
        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # Update the Verifikasi instance
        verifikasi.nomor_kantong = no_kantong
        verifikasi.jenis_kantong = jenis_kantong
        verifikasi.pengambilan = pengambilan
        verifikasi.stop_cc = int(stop_cc) if stop_cc and str(stop_cc).isdigit() else None
        verifikasi.diambil_sebanyak = diambil_sebanyak
        verifikasi.reaksi_donor = reaksi_donor if reaksi_donor else None
        
        if petugas_aftap_id:
            petugas_aftap_instance = get_object_or_404(Petugas, id=petugas_aftap_id)
            verifikasi.petugas_aftap = petugas_aftap_instance

        verifikasi.save()

        return JsonResponse({'success': True, 'message': 'Data aftap berhasil disimpan.'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': f'Terjadi kesalahan pada server: {str(e)}'}, status=500)

from django.http import HttpResponse

from reportlab.pdfgen import canvas

from reportlab.lib.pagesizes import letter

from reportlab.lib.units import inch



# ... (existing imports) ...



from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import PageBreak # Add this import

def generate_donor_pdf(request, verifikasi_id):
    verifikasi = get_object_or_404(Verifikasi, id=verifikasi_id)
    pendonor = verifikasi.pendonor

    print(f"Generating PDF for verifikasi {verifikasi.id}. Aftap data from Verifikasi object:")
    print(f"  nomor_kantong: {verifikasi.nomor_kantong}")
    print(f"  jenis_kantong: {verifikasi.jenis_kantong}")
    print(f"  pengambilan: {verifikasi.pengambilan}")
    print(f"  stop_cc: {verifikasi.stop_cc}")
    print(f"  diambil_sebanyak: {verifikasi.diambil_sebanyak}")
    print(f"  reaksi_donor: {verifikasi.reaksi_donor}")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="formulir_{pendonor.nama}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, topMargin=1.5 * inch)
    styles = getSampleStyleSheet()
    # Create a centered style for the heading
    h2_centered = styles['h2']
    h2_centered.alignment = TA_CENTER

    # Define a ParagraphStyle for the address to ensure wrapping
    address_style = styles['Normal']
    address_style.fontSize = 10 # Adjust font size if needed
    address_style.leading = 12 # Line spacing

    story = []

    def my_header(canvas, doc):
        canvas.saveState()
        width, height = letter


        
        # Logo
        logo_path = 'myapp/static/images/Lambang_Kabupaten_Bintan.png'
        try:
            # Get absolute path to the logo
            from django.conf import settings
            import os
            abs_logo_path = os.path.join(settings.BASE_DIR, logo_path)

            logo_width = 1.0 * inch  # Ukuran logo disesuaikan
            logo_height = 1.0 * inch # Ukuran logo disesuaikan
            logo_x = inch + 0.2 * inch
            logo_y = height - 1.45 * inch # Sesuaikan posisi Y agar logo rata tengah vertikal dengan teks (dinaikkan sedikit)

            canvas.drawImage(abs_logo_path, logo_x, logo_y, width=logo_width, height=logo_height)
        except Exception as e:
            print(f"Error drawing local logo: {e}")
            # Draw a placeholder if logo fails
            logo_size = 0.7 * inch
            logo_x = inch + 0.2 * inch
            logo_y = height - 1.1 * inch
            canvas.rect(logo_x, logo_y, logo_size, logo_size)
            canvas.setFont('Helvetica', 8)
            canvas.drawCentredString(logo_x + logo_size / 2, logo_y + logo_size / 2 - 4, "LOGO")

        # Teks kop surat (sejajar dengan logo)
        text_start_x = logo_x + logo_width + 0.2 * inch # Mulai teks setelah logo + spasi
        text_center_x = text_start_x + (width - inch - text_start_x) / 2.0 # Tengah relatif terhadap sisa lebar

        canvas.setFont('Helvetica', 14) # Tidak di-bold
        canvas.drawCentredString(text_center_x, height - 0.8 * inch, "PEMERINTAH KABUPATEN BINTAN")
        canvas.setFont('Helvetica-Bold', 14) # DINAS KESEHATAN di-bold
        canvas.drawCentredString(text_center_x, height - 1.0 * inch, "DINAS KESEHATAN")
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawCentredString(text_center_x, height - 1.25 * inch, "RSUD KABUPATEN BINTAN")
        canvas.setFont('Helvetica', 10)
        canvas.drawCentredString(text_center_x, height - 1.45 * inch, "Jl. Kesehatan No. 1, Kijang Kota, Kec. Bintan Timur, Kab. Bintan, Kepulauan Riau")
        canvas.drawCentredString(text_center_x, height - 1.6 * inch, "Telepon (0771) 4623514, Email : rsud.bintan@yahoo.com")

        # Garis kop surat
        canvas.setStrokeColorRGB(0, 0, 0)
        canvas.setLineWidth(2)
        canvas.line(inch, height - 1.7 * inch, width - inch, height - 1.7 * inch) # Sesuaikan posisi garis
        canvas.setLineWidth(1)
        canvas.line(inch, height - 1.72 * inch, width - inch, height - 1.72 * inch) # Sesuaikan posisi garis
        
        canvas.restoreState()





    story.append(Spacer(1, 0.2 * inch))
    # --- IDENTITAS PENDONOR ---
    # Create a single-cell table for the heading to apply background color
    heading_table_data = [[Paragraph("IDENTITAS PENDONOR", h2_centered)]]
    heading_table = Table(heading_table_data, colWidths=[6.5 * inch]) # Span full content width
    heading_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.Color(0.95, 0.95, 0.95)), # Even lighter gray
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('VALIGN', (0,0), (0,0), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (0,0), 6),
        ('TOPPADDING', (0,0), (0,0), 6),
        ('LINEABOVE', (0,0), (-1,0), 0.5, colors.black), # Top border
        ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.black), # Bottom border
    ]))
    story.append(heading_table)

    # Construct full address
    full_address_parts = [pendonor.alamat_rumah]
    if pendonor.rt_rw:
        full_address_parts.append(f"RT/RW {pendonor.rt_rw}")
    if pendonor.kelurahan:
        full_address_parts.append(f"Kel. {pendonor.kelurahan}")
    if pendonor.kecamatan:
        full_address_parts.append(f"Kec. {pendonor.kecamatan}")
    if pendonor.kab_kota:
        full_address_parts.append(f"{pendonor.kab_kota}")
    full_address = ", ".join(filter(None, full_address_parts))

    # Two-column data layout with specific field placement
    pendonor_data = [
        # Label1, Colon1, Value1, Label2, Colon2, Value2
        ['Tanggal', ':', f'{pendonor.tgl.strftime("%d %b %Y") if pendonor.tgl else "-"}',
         'Jam', ':', f'{pendonor.waktu.strftime("%H:%M") if pendonor.waktu else "-"}'],

        ['Nama', ':', f'{pendonor.nama.title()}',
         'Tanggal Terakhir Donor', ':', f'{pendonor.tgl_donor_terakhir.strftime("%d %b %Y") if pendonor.tgl_donor_terakhir else "-"}'],

        ['NIK', ':', f'{pendonor.nik_ktp if pendonor.nik_ktp else "-"}',
         'Golongan Darah', ':', f'{pendonor.golongan_darah} Rhesus: {pendonor.rhesus}'],

        ['Tanggal Lahir', ':', f'{pendonor.tanggal_lahir.strftime("%d %b %Y") if pendonor.tanggal_lahir else "-"}',
         'Jenis Kelamin', ':', f'{pendonor.jenis_kelamin if pendonor.jenis_kelamin else "-"}'],

        ['Pekerjaan', ':', f'{pendonor.pekerjaan if pendonor.pekerjaan else "-"}',
         'No. Telepon', ':', f'{pendonor.no_telepon if pendonor.no_telepon else "-"}'],

        ['Alamat Rumah', ':', Paragraph(f'{full_address if full_address else "-"}', address_style),
         '', '', ''],
    ]

    col_widths = [1.4 * inch, 0.1 * inch, 2.05 * inch, 1.6 * inch, 0.1 * inch, 1.25 * inch]
    pendonor_table = Table(pendonor_data, colWidths=col_widths)

    pendonor_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        # Bold labels
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), # Labels in first column
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'), # Labels in fourth column
        # Add grid lines
    ]))

    story.append(pendonor_table)
    story.append(Spacer(1, 0.25 * inch))

    # --- VERIFIKASI PETUGAS ---
    # Create a single-cell table for the heading to apply background color
    verifikasi_heading_table_data = [[Paragraph("VERIFIKASI PETUGAS", h2_centered)]]
    verifikasi_heading_table = Table(verifikasi_heading_table_data, colWidths=[6.5 * inch]) # Span full content width
    verifikasi_heading_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.Color(0.95, 0.95, 0.95)), # Even lighter gray
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('VALIGN', (0,0), (0,0), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (0,0), 6),
        ('TOPPADDING', (0,0), (0,0), 6),
        ('LINEABOVE', (0,0), (-1,0), 0.5, colors.black), # Top border
        ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.black), # Bottom border
    ]))
    story.append(verifikasi_heading_table)
    story.append(Spacer(1, 0.1 * inch)) # Tambahkan spasi di sini

    # --- VERIFIKASI DATA ---
    verifikasi_data = [
        ['Nama Petugas', f': {verifikasi.nama_petugas if verifikasi.nama_petugas else (verifikasi.petugas.nama if verifikasi.petugas else "-")}',
         'Status Pendonor', f': {"Pendonor Baru" if pendonor.tgl_donor_terakhir is None else "Pendonor Lama"}'],
        ['Lokasi Donor', f': {verifikasi.jenis_donasi if verifikasi.jenis_donasi else "-"}',
         'Jenis Donor', f': {verifikasi.jenis_donor if verifikasi.jenis_donor else "-"}'],
    ]

    verifikasi_col_widths = [1.5 * inch, 2.5 * inch, 1.5 * inch, 1.0 * inch] # Total 6.5 inch

    verifikasi_table = Table(verifikasi_data, colWidths=verifikasi_col_widths)
    verifikasi_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        # Bold labels
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ]))
    story.append(verifikasi_table)
    story.append(Spacer(1, 0.1 * inch)) # Mengembalikan spasi ke 0.1 inch

    # Add a horizontal line
    line_table = Table([['']], colWidths=[6.5 * inch]) # Lebar penuh konten
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.black), # Garis bawah
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 0.1 * inch))

    # --- HASIL PEMERIKSAAN FISIK ---
    physical_exam_details = []
    
    # HB Value
    if verifikasi.hb_value is not None:
        hb_reason = 'Sesuai'
        if verifikasi.hb_value < 12.5:
            hb_reason = f'Tidak Sesuai (< 12.5)'
        elif verifikasi.hb_value > 17:
            hb_reason = f'Tidak Sesuai (> 17)'
        physical_exam_details.append(['HB', ':', f'{verifikasi.hb_value}', hb_reason])

    # Tensi
    if verifikasi.tensi:
        tensi_reason = 'Sesuai'
        try:
            systolic, diastolic = map(int, verifikasi.tensi.split('/'))
            if systolic < 110 or diastolic < 70:
                tensi_reason = 'Tidak Sesuai (< 110/70)'
            if systolic > 150 or diastolic > 100:
                tensi_reason = 'Tidak Sesuai (> 150/100)'
        except ValueError:
            tensi_reason = 'Format Tidak Valid'
        physical_exam_details.append(['Tensi', ':', f'{verifikasi.tensi}', tensi_reason])

    # Berat Badan
    if verifikasi.berat_badan is not None:
        bb_reason = 'Sesuai'
        if verifikasi.berat_badan < 50:
            bb_reason = 'Tidak Sesuai (< 50 Kg)'
        physical_exam_details.append(['Berat Badan', ':', f'{verifikasi.berat_badan} Kg', bb_reason])

    # Suhu Badan
    if verifikasi.suhu_badan is not None:
        physical_exam_details.append(['Suhu Badan', ':', f'{verifikasi.suhu_badan} °C', 'Sesuai'])
    
    # Nadi
    if verifikasi.nadi is not None:
        physical_exam_details.append(['Nadi', ':', f'{verifikasi.nadi} bpm', 'Sesuai'])

    if physical_exam_details:
        pemeriksaan_table = Table(physical_exam_details, colWidths=[1.5 * inch, 0.1 * inch, 2.4 * inch, 2.5 * inch])
        pemeriksaan_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        story.append(pemeriksaan_table)

        # Add a horizontal line after physical exam details
        line_table_pemeriksaan = Table([['']], colWidths=[6.5 * inch]) # Lebar penuh konten
        line_table_pemeriksaan.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.black), # Garis bawah
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(line_table_pemeriksaan)
        story.append(Spacer(1, 0.1 * inch)) # Sedikit spasi setelah garis

    story.append(Spacer(1, 0.1 * inch)) # Mengurangi spasi

    aftap_details = []

    # Prepare data for left column
    no_kantong_val = verifikasi.nomor_kantong if verifikasi.nomor_kantong else "-"
    jenis_kantong_val = verifikasi.jenis_kantong if verifikasi.jenis_kantong else "-"
    diambil_sebanyak_val = verifikasi.diambil_sebanyak if verifikasi.diambil_sebanyak else "-"

    # Prepare data for right column
    pengambilan_val = verifikasi.pengambilan if verifikasi.pengambilan else "-"
    if verifikasi.pengambilan == 'Stop' and verifikasi.stop_cc:
        pengambilan_val += f' ({verifikasi.stop_cc} cc)'
    reaksi_donor_val = verifikasi.reaksi_donor if verifikasi.reaksi_donor else "-"

    # Combine into 2x2 layout
    aftap_details_formatted = []
    aftap_details_formatted.append(['No Kantong', ':', no_kantong_val, 'Pengambilan', ':', pengambilan_val])
    aftap_details_formatted.append(['Jenis Kantong', ':', jenis_kantong_val, 'Reaksi Donor', ':', reaksi_donor_val])
    aftap_details_formatted.append(['Diambil Sebanyak', ':', diambil_sebanyak_val, '', '', '']) # Kosongkan kolom kanan bawah

    if aftap_details_formatted: # Check if there's any data to display
        aftap_table = Table(aftap_details_formatted, colWidths=[1.5 * inch, 0.1 * inch, 2.4 * inch, 1.5 * inch, 0.1 * inch, 0.9 * inch]) # Total 6.5 inch
        aftap_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), # Labels in first and fourth column
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ]))
        story.append(aftap_table)

    story.append(Spacer(1, 0.25 * inch))

    story.append(PageBreak()) # Tambahkan halaman baru

    # --- HASIL KUESIONER ---
    story.append(Spacer(1, 0.2 * inch))
    
    # Heading for the section
    kuesioner_heading_data = [[Paragraph("HASIL KUESIONER", h2_centered)]]
    kuesioner_heading_table = Table(kuesioner_heading_data, colWidths=[6.5 * inch])
    kuesioner_heading_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.Color(0.95, 0.95, 0.95)),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('VALIGN', (0,0), (0,0), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (0,0), 6),
        ('TOPPADDING', (0,0), (0,0), 6),
        ('LINEABOVE', (0,0), (-1,0), 0.5, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.black),
    ]))
    story.append(kuesioner_heading_table)
    story.append(Spacer(1, 0.1 * inch))

    kuesioner_details = []
    question_texts = [
        "Apakah Anda merasa sehat hari ini?",
        "Apakah Anda sedang minum obat penghilang nyeri?",
        "Apakah Anda memiliki riwayat Diabetes?",
        "Apakah Anda memiliki riwayat Ginjal?",
        "Apakah Anda memiliki riwayat Gangguan darah?",
        "Apakah Anda memiliki riwayat Malaria?",
        "Apakah Anda memiliki riwayat Ashma/sesak nafas?",
        "Apakah Anda memiliki riwayat Alergi?",
        "Apakah Anda memiliki riwayat TBC?",
        "Apakah Anda memiliki riwayat Hepatitis/Sakit Kuning?",
        "Apakah Anda memiliki riwayat Jantung?",
        "Apakah Anda sering pingsan/kejang-kejang?",
        "Apakah Anda mempunyai gejala kemungkinan pengidap HIV?",
        "Apakah Anda melakukan tindik telinga/tato dalam 6 bulan terakhir?",
        "Apakah Anda pernah keluar daerah dalam 3 bulan terakhir?",
        "Apakah Anda dalam 3 minggu terakhir cabut gigi?",
        "Apakah Anda pernah menyumbangkan darah dengan memakai identitas lain?",
        "Apakah Anda pernah menyumbangkan darah dalam waktu kurang dari 3 bulan?",
        "Apakah Anda dalam kondisi hamil/menyusui/haid/habis melahirkan?",
    ]

    if verifikasi.is_manual_input:
        answers = ['Iya'] + ['Tidak'] * (len(question_texts) - 1)
        # Specifically handle question 11 for gender if needed, but for now, default is "Tidak"
        if pendonor.jenis_kelamin == 'Laki-laki':
            answers[18] = "-" # The last question is for women
        
        questions = list(zip(question_texts, answers))
    else:
        # List of questions and their corresponding fields in the Verifikasi model
        questions = [
            (question_texts[0], verifikasi.q1_sehat_hari_ini),
            (question_texts[1], verifikasi.q2_minum_obat),
            (question_texts[2], verifikasi.q3a_diabetes),
            (question_texts[3], verifikasi.q3b_ginjal),
            (question_texts[4], verifikasi.q3c_gangguan_darah),
            (question_texts[5], verifikasi.q3d_malaria),
            (question_texts[6], verifikasi.q3e_ashma),
            (question_texts[7], verifikasi.q3f_alergi),
            (question_texts[8], verifikasi.q3g_tbc),
            (question_texts[9], verifikasi.q3h_hepatitis),
            (question_texts[10], verifikasi.q3i_jantung),
            (question_texts[11], verifikasi.q4_pingsan_kejang),
            (question_texts[12], verifikasi.q5_gejala_hiv),
            (question_texts[13], verifikasi.q6_tindik_tato),
            (question_texts[14], verifikasi.q7_keluar_daerah),
            (question_texts[15], verifikasi.q8_cabut_gigi),
            (question_texts[16], verifikasi.q9_identitas_lain),
            (question_texts[17], verifikasi.q10_donor_kurang_3_bulan),
            (question_texts[18], verifikasi.q11_wanita_kondisi),
        ]

    for i, (question, answer) in enumerate(questions):
        # For manual input, if it's the last question and the donor is male, skip it.
        if verifikasi.is_manual_input and i == 18 and pendonor.jenis_kelamin == 'Laki-laki':
            continue
        kuesioner_details.append([f"{i+1}.", Paragraph(question, styles['Normal']), answer if answer else "-"])

    if kuesioner_details:
        kuesioner_table = Table(kuesioner_details, colWidths=[0.3 * inch, 4.5 * inch, 1.7 * inch]) # Total 6.5 inch
        kuesioner_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),  # Kolom 0 dan 1 rata kiri
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'), # Kolom 2 rata kanan
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ]))
        story.append(kuesioner_table)
        story.append(Spacer(1, 0.2 * inch))

    if verifikasi.alasan_tidak_layak:
        story.append(Paragraph(f"<b>Alasan Tidak Layak:</b> {verifikasi.alasan_tidak_layak.replace('\n', '<br/>')}", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

    story.append(Spacer(1, 0.25 * inch))

    doc.build(story, onFirstPage=my_header, onLaterPages=my_header)
    return response

@csrf_exempt
def get_donor_history(request, nik_ktp):
    pendonor_list = Pendonor.objects.filter(nik_ktp=nik_ktp)

    if not pendonor_list.exists():
        return JsonResponse({'success': False, 'error': 'Pendonor dengan NIK tersebut tidak ditemukan.'}, status=404)

    verifikasi_list = Verifikasi.objects.filter(pendonor__in=pendonor_list, is_verified=True).order_by('-timestamp')

    if not verifikasi_list.exists():
        return JsonResponse({'success': False, 'error': 'Riwayat verifikasi tidak ditemukan.'}, status=404)

    # Count successful donations
    donation_count = verifikasi_list.filter(keputusan_petugas='Lanjut Donor').count()

    # Get the last donation date from the Pendonor object
    pendonor_instance = pendonor_list.first() # Get the primary Pendonor instance for this NIK
    last_donation_date = None
    if pendonor_instance and pendonor_instance.tgl_donor_terakhir:
        last_donation_date = pendonor_instance.tgl_donor_terakhir.strftime("%d %b %Y")

    history_records = []
    jakarta_tz = ZoneInfo("Asia/Jakarta") # Define Jakarta timezone once
    for verifikasi in verifikasi_list:
        physical_exam_details = []
        alasan_fisik_list = []
        
        # HB Value
        if verifikasi.hb_value is not None:
            hb_reason = 'Sesuai'
            if verifikasi.hb_value < 12.5 or verifikasi.hb_value > 17:
                hb_reason = 'Tidak Sesuai'
            physical_exam_details.append({'field': 'HB', 'value': str(verifikasi.hb_value), 'reason': hb_reason})

        # Tensi
        if verifikasi.tensi:
            tensi_reason = 'Sesuai'
            try:
                systolic, diastolic = map(int, verifikasi.tensi.split('/'))
                if systolic < 110 or diastolic < 70 or systolic > 150 or diastolic > 100:
                    tensi_reason = 'Tidak Sesuai'
            except ValueError:
                tensi_reason = 'Format Tidak Valid'
            physical_exam_details.append({'field': 'Tensi', 'value': verifikasi.tensi, 'reason': tensi_reason})

        # Berat Badan
        if verifikasi.berat_badan is not None:
            bb_reason = 'Sesuai'
            if verifikasi.berat_badan < 50:
                bb_reason = 'Tidak Sesuai'
            physical_exam_details.append({'field': 'Berat Badan', 'value': str(verifikasi.berat_badan) + ' Kg', 'reason': bb_reason})

        # Suhu Badan
        if verifikasi.suhu_badan is not None:
            physical_exam_details.append({'field': 'Suhu Badan', 'value': str(verifikasi.suhu_badan) + ' °C', 'reason': 'Sesuai'})
        
        # Nadi
        if verifikasi.nadi is not None:
            physical_exam_details.append({'field': 'Nadi', 'value': str(verifikasi.nadi) + ' bpm', 'reason': 'Sesuai'})

        overall_alasan = []
        if verifikasi.alasan_tidak_layak:
            overall_alasan.append(verifikasi.alasan_tidak_layak)
        if alasan_fisik_list: # This list is not populated in this view, but kept for consistency
            overall_alasan.extend(alasan_fisik_list)
        
        is_eligible = not overall_alasan # This is based on alasan_tidak_layak from kuesioner and physical_exam_details from save_verifikasi_lanjut_data

        current_nama_petugas = verifikasi.nama_petugas if verifikasi.nama_petugas else (verifikasi.petugas.nama if verifikasi.petugas else '-')
        current_nama_petugas_aftap = verifikasi.petugas_aftap.nama if verifikasi.petugas_aftap else '-'
        print(f"Debug: nama_petugas={current_nama_petugas}, nama_petugas_aftap={current_nama_petugas_aftap}")

        display_date_only = '-'
        display_time_only = '-'

        if verifikasi.is_manual_input:
            if verifikasi.pendonor.tgl_donor_terakhir:
                display_date_only = verifikasi.pendonor.tgl_donor_terakhir.strftime("%d %b %Y")
            elif verifikasi.timestamp: # Fallback
                display_date_only = verifikasi.timestamp.strftime("%d %b %Y")
            # Time is not relevant for manually entered old data, so we can leave it as '-'
        elif verifikasi.timestamp:
            local_timestamp = verifikasi.timestamp.astimezone(jakarta_tz)
            display_date_only = local_timestamp.strftime("%d %b %Y")
            display_time_only = local_timestamp.strftime("%H:%M")

        history_record_data = {
            'tgl_display': display_date_only,
            'waktu_display': display_time_only,
            'status': verifikasi.keputusan_petugas if verifikasi.keputusan_petugas else ('Layak' if is_eligible else 'Tidak Layak'),
            'nama_petugas': current_nama_petugas,
            'nama_petugas_aftap': current_nama_petugas_aftap,
            'alasan_kuesioner': verifikasi.alasan_tidak_layak or '',
            'physical_exam_details': physical_exam_details, # Now populated
            'catatan_dokter': verifikasi.catatan_dokter or '',
            'overall_eligibility': 'Layak' if is_eligible else 'Tidak Layak',
            'all_reasons': '\n'.join(overall_alasan),
            'pengambilan': verifikasi.pengambilan,
            'reaksi_donor': verifikasi.reaksi_donor,
            'verifikasi_id': verifikasi.id,
            'pdf_url': f'/generate-pdf/{verifikasi.id}/',
            'no_kantong_aftap': verifikasi.nomor_kantong or '',
            'jenis_kantong': verifikasi.jenis_kantong or '',
            'stop_cc': verifikasi.stop_cc or '',
            'diambil_sebanyak': verifikasi.diambil_sebanyak or '',
        }
        history_records.append(history_record_data)

    response_data = {
        'success': True,
        'pendonor_name': pendonor_list.first().nama.title(),
        'history_records': history_records,
        'donation_count': donation_count,
        'last_donation_date': last_donation_date,
    }

    return JsonResponse(response_data)

def panggil_pendonor_view(request):
    seventy_five_days_ago = timezone.now().date() - timedelta(days=75)

    # Subquery to get the timestamp and keputusan_petugas of the LATEST Verifikasi for each Pendonor
    latest_verifikasi_subquery = Verifikasi.objects.filter(
        pendonor=OuterRef('pk')
    ).order_by('-timestamp').values('timestamp', 'keputusan_petugas')[:1]

    pendonor_to_call = Pendonor.objects.annotate(
        latest_verifikasi_timestamp=Subquery(latest_verifikasi_subquery.values('timestamp')),
        latest_keputusan_petugas=Subquery(latest_verifikasi_subquery.values('keputusan_petugas'))
    ).filter(
        tgl_donor_terakhir__lt=seventy_five_days_ago, # Last successful donation was more than 75 days ago
        latest_keputusan_petugas='Lanjut Donor' # Their most recent verification was 'Lanjut Donor'
    ).order_by('tgl_donor_terakhir')

    context = {
        'pendonor_to_call': pendonor_to_call,
    }
    return render(request, 'panggil_pendonor.html', context)

def tambah_pendonor_lama_view(request):
    if request.method == 'POST':
        form = FullPendonorVerifikasiForm(request.POST)
        if form.is_valid():
            # Save Pendonor data
            pendonor_data = {
                field: form.cleaned_data[field]
                for field in PendonorForm.Meta.fields
                if field in form.cleaned_data
            }
            pendonor = Pendonor.objects.create(**pendonor_data)

            # Save Verifikasi data
            verifikasi_data = {
                'pendonor': pendonor,
                'is_verified': True,
                'is_manual_input': True,
                'keputusan_petugas': 'Lanjut Donor', # Always 'Lanjut Donor' for this form
                'catatan_dokter': form.cleaned_data.get('catatan_dokter'), # Keep in case it's still needed for some reason
                'jenis_donasi': form.cleaned_data.get('jenis_donasi'),
                'jenis_donor': form.cleaned_data.get('jenis_donor'),
                'hb_value': form.cleaned_data.get('hb_value'),
                'berat_badan': form.cleaned_data.get('berat_badan'),
                'tensi': form.cleaned_data.get('tensi'),
                'nomor_kantong': form.cleaned_data.get('nomor_kantong'),
                'jenis_kantong': form.cleaned_data.get('jenis_kantong'),
                'pengambilan': form.cleaned_data.get('pengambilan'),
                'stop_cc': form.cleaned_data.get('stop_cc'),
                'diambil_sebanyak': form.cleaned_data.get('diambil_sebanyak'),
                'reaksi_donor': form.cleaned_data.get('reaksi_donor'),
            }

            # Handle ForeignKey fields for Petugas
            petugas_aftap = form.cleaned_data.get('petugas_aftap')
            if petugas_aftap:
                verifikasi_data['petugas_aftap'] = petugas_aftap
                verifikasi_data['petugas'] = petugas_aftap # Set petugas for verification to the same value
                verifikasi_data['nama_petugas'] = petugas_aftap.nama # Set nama_petugas for verification


            verifikasi = Verifikasi.objects.create(**verifikasi_data)

            return redirect('myapp:daftar_pendonor') # Redirect to the donor list page
        else:
            # If form is not valid, re-render the template with errors
            all_petugas = Petugas.objects.all()
            context = {
                'form': form,
                'all_petugas': all_petugas
            }
            return render(request, 'tambah_pendonor_lama.html', context)
    
    form = FullPendonorVerifikasiForm()
    all_petugas = Petugas.objects.all()
    context = {
        'form': form,
        'all_petugas': all_petugas
    }
    return render(request, 'tambah_pendonor_lama.html', context)






# ... (rest of the file)
