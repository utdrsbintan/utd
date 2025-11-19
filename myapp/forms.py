from django import forms
from .models import Petugas, Pendonor, Verifikasi
from django.contrib.auth.forms import AuthenticationForm # Import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})

class PetugasForm(forms.ModelForm):
    class Meta:
        model = Petugas
        fields = ['nama', 'nip', 'jabatan']

    def clean_nama(self):
        return self.cleaned_data['nama'].title()

    def clean_jabatan(self):
        return self.cleaned_data['jabatan'].title()

class PendonorForm(forms.ModelForm):
    tgl_donor_terakhir = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
        label="Tanggal Donor Terakhir",
    )

    class Meta:
        model = Pendonor
        fields = ['nama', 'tanggal_lahir', 'jenis_kelamin', 'golongan_darah', 'rhesus', 'nik_ktp', 'alamat_rumah', 'rt_rw', 'kelurahan', 'kecamatan', 'kab_kota', 'pekerjaan', 'no_telepon', 'tgl_donor_terakhir']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'tanggal_lahir': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
            'jenis_kelamin': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'golongan_darah': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'rhesus': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'nik_ktp': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'inputmode': 'numeric', 'pattern': '[0-9]{16}', 'title': 'NIK KTP harus 16 digit angka'}),
            'alamat_rumah': forms.Textarea(attrs={'class': 'form-control', 'required': 'required'}),
            'rt_rw': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'kelurahan': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'kecamatan': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'kab_kota': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'pekerjaan': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'no_telepon': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'type': 'number'}),
            # tgl_donor_terakhir is handled above with required=False
        }
        labels = {
            'nama': 'Nama',
            'tanggal_lahir': 'Tanggal Lahir',
            'jenis_kelamin': 'Jenis Kelamin',
            'golongan_darah': 'Golongan Darah',
            'rhesus': 'Rhesus',
            'nik_ktp': 'NIK KTP',
            'alamat_rumah': 'Alamat Rumah',
            'rt_rw': 'RT/RW',
            'kelurahan': 'Kelurahan',
            'kecamatan': 'Kecamatan',
            'kab_kota': 'Kab/Kota',
            'pekerjaan': 'Pekerjaan',
            'no_telepon': 'Nomor HP',
            'tgl_donor_terakhir': 'Tanggal Donor Terakhir',
        }

    def clean_nik_ktp(self):
        nik_ktp = self.cleaned_data['nik_ktp']
        if not nik_ktp.isdigit():
            raise forms.ValidationError("NIK KTP harus berupa angka.")
        return nik_ktp

    def clean_no_telepon(self):
        no_telepon = self.cleaned_data['no_telepon']
        if not no_telepon.isdigit():
            raise forms.ValidationError("Nomor Telepon harus berupa angka.")
        return no_telepon

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty choices to select fields
        self.fields['golongan_darah'].choices = [('', 'Pilih Golongan Darah')] + list(self.fields['golongan_darah'].choices)
        self.fields['rhesus'].choices = [('', 'Pilih Rhesus')] + list(self.fields['rhesus'].choices)
        self.fields['jenis_kelamin'].choices = [('', 'Pilih Jenis Kelamin')] + list(self.fields['jenis_kelamin'].choices)
        self.fields['pekerjaan'].choices = [('', 'Pilih Pekerjaan')] + list(self.fields['pekerjaan'].choices)

        # Manually order fields
        field_order = [
            'nama',
            'tanggal_lahir',
            'jenis_kelamin',
            'golongan_darah',
            'rhesus',
            'nik_ktp',
            'alamat_rumah',
            'rt_rw',
            'kelurahan',
            'kecamatan',
            'kab_kota',
            'pekerjaan',
            'no_telepon',
            'tgl_donor_terakhir',
        ]
        self.order_fields(field_order)

class FullPendonorVerifikasiForm(PendonorForm):
    # Fields from VerifikasiForm (initial verification)
    jenis_donasi = forms.ChoiceField(
        choices=Verifikasi.JENIS_DONASI_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label="Lokasi Donasi",
        required=True
    )
    jenis_donor = forms.ChoiceField(
        choices=Verifikasi.JENIS_DONOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label="Jenis Donor",
        required=True
    )
    petugas = forms.ModelChoiceField(
        queryset=Petugas.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Nama Petugas Verifikasi",
        required=False
    )
    keputusan_petugas = forms.ChoiceField(
        choices=[('Lanjut Donor', 'Lanjut Donor'), ('Tidak Lanjut', 'Tidak Lanjut')],
        widget=forms.RadioSelect(),
        label="Keputusan Petugas",
        initial='Lanjut Donor',
        required=False
    )
    catatan_dokter = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Catatan Dokter (jika Tidak Lanjut)",
        required=False
    )

    # Physical Exam Fields
    hb_value = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nilai HB', 'required': 'required'}),
        label="HB",
        required=True
    )
    berat_badan = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Berat Badan (kg)', 'required': 'required'}),
        label="Berat Badan",
        required=True
    )
    tensi = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 120/80', 'required': 'required'}),
        label="Tensi",
        required=True
    )

    # Aftap Fields
    nomor_kantong = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        label="No Kantong",
        required=True
    )
    jenis_kantong = forms.ChoiceField(
        choices=[('', 'Pilih Jenis Kantong')] + list(Verifikasi.JENIS_KANTONG_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label="Jenis Kantong",
        required=True
    )
    pengambilan = forms.ChoiceField(
        choices=[('', 'Pilih Pengambilan')] + list(Verifikasi.PENGAMBILAN_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label="Pengambilan",
        required=True
    )
    stop_cc = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Dihentikan pada (cc)",
        required=False
    )
    diambil_sebanyak = forms.ChoiceField(
        choices=[('', 'Pilih Jumlah')] + list(Verifikasi.DIAMBIL_SEBANYAK_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label="Diambil sebanyak",
        required=True
    )
    reaksi_donor = forms.ChoiceField(
        choices=[('', 'Pilih Reaksi Donor')] + Verifikasi.REAKSI_DONOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label="Reaksi Donor",
        required=True
    )
    petugas_aftap = forms.ModelChoiceField(
        queryset=Petugas.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label="Nama Petugas AFTAP",
        required=True,
        empty_label="Pilih Petugas AFTAP"
    )

    class Meta(PendonorForm.Meta):
        # Inherit fields from PendonorForm.Meta
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty choices to select fields for Verifikasi fields
        self.fields['jenis_donasi'].choices = [('', 'Pilih Lokasi Donasi')] + list(Verifikasi.JENIS_DONASI_CHOICES)
        self.fields['jenis_donor'].choices = [('', 'Pilih Jenis Donor')] + list(Verifikasi.JENIS_DONOR_CHOICES)
        
        # Ensure Petugas queryset is available
        self.fields['petugas'].queryset = Petugas.objects.all()
        self.fields['petugas_aftap'].queryset = Petugas.objects.all()

        # Manually order all fields
        field_order = [
            # Pendonor fields
            'nama', 'tanggal_lahir', 'jenis_kelamin', 'golongan_darah', 'rhesus',
            'nik_ktp', 'alamat_rumah', 'rt_rw', 'kelurahan', 'kecamatan',
            'kab_kota', 'pekerjaan', 'no_telepon', 'tgl_donor_terakhir',
            # Initial Verification fields
            'jenis_donasi', 'jenis_donor', 'petugas', 'keputusan_petugas', 'catatan_dokter',
            # Physical Exam fields
            'hb_value', 'berat_badan', 'tensi',
            # Aftap fields
            'nomor_kantong', 'jenis_kantong', 'pengambilan', 'stop_cc',
            'diambil_sebanyak', 'reaksi_donor', 'petugas_aftap',
        ]
        self.order_fields(field_order)

class KuesionerForm(forms.ModelForm):
    riwayat_penyakit_heading = forms.CharField(label="3. Riwayat Penyakit :", required=False, widget=forms.HiddenInput())
    q1_sehat_hari_ini = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="1. Apakah anda sehat pada hari ini?",
        required=True
    )
    q2_minum_obat = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="2. Sedang minum obat penghilang nyeri (aspirin, piroksikam, antibiotik) dalam satu minggu terakhir?",
        required=True
    )
    q3a_diabetes = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="a. Diabetes",
        required=True
    )
    q3b_ginjal = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="b. Ginjal",
        required=True
    )
    q3c_gangguan_darah = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="c. Gangguan darah (hemofilia/talasemia)",
        required=True
    )
    q3d_malaria = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="d. Malaria",
        required=True
    )
    q3e_ashma = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="e. Ashma/sesak nafas",
        required=True
    )
    q3f_alergi = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="f. Alergi",
        required=True
    )
    q3g_tbc = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="g. TBC",
        required=True
    )
    q3h_hepatitis = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="h. Hepatitis/Sakit Kuning",
        required=True
    )
    q3i_jantung = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="i. Jantung",
        required=True
    )
    q4_pingsan_kejang = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="4. Sering pingsan/kejang-kejang?",
        required=True
    )
    q5_gejala_hiv = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="5. Mempunyai gejala kemungkinan pengidap HIV?",
        required=True
    )
    q6_tindik_tato = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="6. Melakukan tindik telinga/tato dalam 6 bulan terakhir?",
        required=True
    )
    q7_keluar_daerah = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="7. Pernah keluar daerah dalam 3 bulan terakhir?",
        required=True
    )
    q8_cabut_gigi = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="8. Dalam 3 minggu terakhir cabut gigi?",
        required=True
    )
    q9_identitas_lain = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="9. Pernah menyumbangkan darah dengan memakai identitas lain?",
        required=True
    )
    q10_donor_kurang_3_bulan = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="10. Pernah menyumbangkan darah dalam waktu kurang dari 3 bulan?",
        required=True
    )
    q11_wanita_kondisi = forms.ChoiceField(
        choices=Verifikasi.JAWABAN_CHOICES,
        widget=forms.RadioSelect,
        label="11. Bagi wanita: apakah anda dalam kondisi hamil/menyusui/haid/habis melahirkan?",
        required=True
    )

    class Meta:
        model = Verifikasi
        fields = [
            'q1_sehat_hari_ini',
            'q2_minum_obat',
            'q3a_diabetes',
            'q3b_ginjal',
            'q3c_gangguan_darah',
            'q3d_malaria',
            'q3e_ashma',
            'q3f_alergi',
            'q3g_tbc',
            'q3h_hepatitis',
            'q3i_jantung',
            'q4_pingsan_kejang',
            'q5_gejala_hiv',
            'q6_tindik_tato',
            'q7_keluar_daerah',
            'q8_cabut_gigi',
            'q9_identitas_lain',
            'q10_donor_kurang_3_bulan',
            'q11_wanita_kondisi',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the dummy field for heading display
        self.fields['riwayat_penyakit_heading'] = forms.CharField(label="3. Riwayat Penyakit :", required=False, widget=forms.HiddenInput())
        # Manually reorder fields to place the heading correctly
        field_order = [
            'q1_sehat_hari_ini',
            'q2_minum_obat',
            'riwayat_penyakit_heading',
            'q3a_diabetes',
            'q3b_ginjal',
            'q3c_gangguan_darah',
            'q3d_malaria',
            'q3e_ashma',
            'q3f_alergi',
            'q3g_tbc',
            'q3h_hepatitis',
            'q3i_jantung',
            'q4_pingsan_kejang',
            'q5_gejala_hiv',
            'q6_tindik_tato',
            'q7_keluar_daerah',
            'q8_cabut_gigi',
            'q9_identitas_lain',
            'q10_donor_kurang_3_bulan',
            'q11_wanita_kondisi',
        ]
        self.order_fields(field_order)
class VerifikasiForm(forms.Form):
    JENIS_DONASI_CHOICES = [
        ('', 'Pilih Lokasi Donasi'),
        ('Dalam Gedung', 'Dalam Gedung'),
        ('Luar Gedung', 'Luar Gedung'),
    ]
    JENIS_DONOR_CHOICES = [
        ('', 'Pilih Jenis Donor'),
        ('Sukarela', 'Sukarela'),
        ('Pengganti', 'Pengganti'),
    ]
    STATUS_PENDONOR_CHOICES = [
        ('Pendonor Baru', 'Pendonor Baru'),
        ('Pendonor Lama', 'Pendonor Lama'),
    ]

    jenis_donasi = forms.ChoiceField(
        choices=JENIS_DONASI_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label="Lokasi Donasi",
    )
    jenis_donor = forms.ChoiceField(
        choices=JENIS_DONOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        label="Jenis Donor",
    )
    status_pendonor = forms.ChoiceField(
        choices=STATUS_PENDONOR_CHOICES,
        widget=forms.RadioSelect(attrs={'required': 'required'}),
        label="Status Pendonor",
    )

class VerifikasiLanjutForm(forms.ModelForm):
    class Meta:
        model = Verifikasi
        fields = ['hb_value', 'berat_badan', 'tensi']
        widgets = {
            'hb_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nilai HB'}),
            'berat_badan': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Berat Badan (kg)'}),
            'tensi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 120/80'}),
        }