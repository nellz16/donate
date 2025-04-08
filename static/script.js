// static/script.js

// Fungsi formatRupiah: Menambahkan titik pemisah ribuan secara otomatis
function formatRupiah(input) {
    // Hilangkan karakter non-digit
    let angka = input.value.replace(/\D/g, '');
    let formatted = '';
    while (angka.length > 3) {
        let chunk = angka.slice(-3);
        angka = angka.slice(0, -3);
        formatted = '.' + chunk + formatted;
    }
    formatted = angka + formatted;
    input.value = formatted;
}

// Event listener untuk checkbox opsi anonim
document.getElementById('anon').addEventListener('change', function(){
    let nameInput = document.getElementById('name');
    if(this.checked) {
        nameInput.value = "Anonim";
        nameInput.disabled = true;
    } else {
        nameInput.disabled = false;
        nameInput.value = "";
    }
});
