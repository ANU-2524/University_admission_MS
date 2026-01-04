document.addEventListener('DOMContentLoaded', function(){
  const input = document.getElementById('searchInput');
  if(input){
    input.addEventListener('input', function(){
      const q = this.value.toLowerCase();
      const rows = document.querySelectorAll('#applicantsTable tbody tr');
      rows.forEach(r => {
        const name = r.querySelector('.name-col').textContent.toLowerCase();
        r.style.display = name.includes(q) ? '' : 'none';
      });
    });
  }
});

function confirmApprove(){
  return confirm('Approve documents and confirm admission?');
}
function confirmReject(){
  return confirm('Reject documents and cancel admission?');
}
