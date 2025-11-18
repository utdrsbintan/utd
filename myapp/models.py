from django.db import models

class Petugas(models.Model):
    nama = models.CharField(max_length=100)
    nip = models.CharField(max_length=20, unique=True)
    jabatan = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Pendonor(models.Model):
    GOLONGAN_DARAH_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O'),
    ]
    RHESUS_CHOICES = [
        ('Positif', 'Positif'),
        ('Negatif', 'Negatif'),
    ]
    JENIS_KELAMIN_CHOICES = [
        ('Laki-laki', 'Laki-laki'),
        ('Perempuan', 'Perempuan'),
    ]

    PEKERJAAN_CHOICES = [
        ('TNI', 'TNI'),
        ('POLRI', 'POLRI'),
        ('ASN', 'ASN'),
        ('BUMN', 'BUMN'),
        ('Mahasiswa', 'Mahasiswa'),
        ('Pelajar', 'Pelajar'),
        ('Pegawai Swasta', 'Pegawai Swasta'),
        ('Petani', 'Petani'),
        ('Buruh', 'Buruh'),
        ('Nelayan', 'Nelayan'),
        ('Wiraswasta', 'Wiraswasta'),
        ('Lain-lain', 'Lain-lain'),
    ]

    nama = models.CharField(max_length=100)
    tanggal_lahir = models.DateField(null=True, blank=True)
    jenis_kelamin = models.CharField(max_length=10, choices=JENIS_KELAMIN_CHOICES, null=True, blank=True)
    golongan_darah = models.CharField(max_length=2, choices=GOLONGAN_DARAH_CHOICES, null=True, blank=True)
    rhesus = models.CharField(max_length=8, choices=RHESUS_CHOICES, null=True, blank=True)
    nik_ktp = models.CharField(max_length=16, null=True, blank=True)
    alamat_rumah = models.TextField(null=True, blank=True)
    rt_rw = models.CharField(max_length=10, null=True, blank=True)
    kelurahan = models.CharField(max_length=100, null=True, blank=True)
    kecamatan = models.CharField(max_length=100, null=True, blank=True)
    kab_kota = models.CharField(max_length=100, null=True, blank=True)
    pekerjaan = models.CharField(max_length=100, choices=PEKERJAAN_CHOICES, null=True, blank=True)
    no_telepon = models.CharField(max_length=15, null=True, blank=True)
    tgl_donor_terakhir = models.DateField(null=True, blank=True)
    tgl = models.DateField(auto_now_add=True)
    waktu = models.TimeField(auto_now_add=True) # New field for automatic time recording
    def __str__(self):
        return self.nama

class Verifikasi(models.Model):
    JAWABAN_CHOICES = [
        ('Iya', 'Iya'), ('Tidak', 'Tidak')
    ]
    HB_CHOICES = [
        ('Normal', 'Normal'), ('Rendah', 'Rendah'), ('Tinggi', 'Tinggi')
    ]
    JENIS_DONASI_CHOICES = [
        ('Dalam Gedung', 'Dalam Gedung'),
        ('Luar Gedung', 'Luar Gedung'),
    ]
    JENIS_DONOR_CHOICES = [
        ('Sukarela', 'Sukarela'),
        ('Pengganti', 'Pengganti'),
    ]
    JENIS_KANTONG_CHOICES = [
        ('350 double', '350 double'),
        ('350 triple', '350 triple'),
        ('250 double', '250 double'),
    ]
    PENGAMBILAN_CHOICES = [
        ('Baik', 'Baik'),
        ('Tidak Lancar', 'Tidak Lancar'),
        ('Stop', 'Stop'),
    ]
    REAKSI_DONOR_CHOICES = [
        ('Tidak Ada', 'Tidak Ada'),
        ('Pusing', 'Pusing'),
        ('Pingsan', 'Pingsan'),
        ('Bocor', 'Bocor'),
        ('Mual', 'Mual'),
        ('Kram', 'Kram'),
        ('Lainnya', 'Lainnya'),
    ]
    DIAMBIL_SEBANYAK_CHOICES = [
        ('250 cc', '250 cc'),
        ('350 cc', '350 cc'),
    ]

    pendonor = models.ForeignKey(Pendonor, on_delete=models.CASCADE)
    # Questionnaire fields
    q1_sehat_hari_ini = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q2_minum_obat = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q3a_diabetes = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q3b_ginjal = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q3c_gangguan_darah = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q3d_malaria = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q3e_ashma = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q3f_alergi = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q3g_tbc = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q3h_hepatitis = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q3i_jantung = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q4_pingsan_kejang = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q5_gejala_hiv = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q6_tindik_tato = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q7_keluar_daerah = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q8_cabut_gigi = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q9_identitas_lain = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q10_donor_kurang_3_bulan = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)
    q11_wanita_kondisi = models.CharField(max_length=5, choices=JAWABAN_CHOICES, null=True, blank=True)

    # Physical exam fields
    hb = models.CharField(max_length=10, choices=[('Normal', 'Normal'), ('Rendah', 'Rendah'), ('Tinggi', 'Tinggi')], null=True, blank=True)
    hb_value = models.FloatField(null=True, blank=True)
    berat_badan = models.FloatField(null=True, blank=True)
    suhu_badan = models.FloatField(null=True, blank=True)
    tensi = models.CharField(max_length=10, null=True, blank=True)
    nadi = models.IntegerField(null=True, blank=True)

    alasan_tidak_layak = models.TextField(blank=True, null=True)

    # Final verification fields
    keputusan_petugas = models.CharField(max_length=20, null=True, blank=True)
    catatan_dokter = models.TextField(null=True, blank=True)
    petugas = models.ForeignKey(Petugas, on_delete=models.SET_NULL, null=True, blank=True)
    nama_petugas = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_manual_input = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True, null=True, blank=True)
    nomor_kantong = models.CharField(max_length=50, null=True, blank=True)
    jenis_donasi = models.CharField(max_length=20, null=True, blank=True) # New field for Lokasi Donor
    jenis_donor = models.CharField(max_length=20, null=True, blank=True) # New field for Jenis Donor

    # Aftap fields
    jenis_kantong = models.CharField(max_length=20, null=True, blank=True)
    pengambilan = models.CharField(max_length=20, null=True, blank=True)
    stop_cc = models.IntegerField(null=True, blank=True)
    diambil_sebanyak = models.CharField(max_length=20, null=True, blank=True)
    reaksi_donor = models.CharField(max_length=50, choices=REAKSI_DONOR_CHOICES, null=True, blank=True)
    petugas_aftap = models.ForeignKey(Petugas, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifikasi_aftap')

    def __str__(self):
        return f"Verifikasi {self.pendonor.nama}"