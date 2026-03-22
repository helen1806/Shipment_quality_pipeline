
  const dropArea = document.getElementById('drop-area');
  const fileInput = document.getElementById('file-input');
  const display   = document.getElementById('file-name-display');

  fileInput.addEventListener('change', () => {
    const names = Array.from(fileInput.files).map(f => f.name).join(', ');
    display.textContent = names ? '✓ ' + names : '';
  });

  ['dragenter','dragover'].forEach(e => {
    dropArea.addEventListener(e, ev => { ev.preventDefault(); dropArea.classList.add('dragover'); });
  });
  ['dragleave','drop'].forEach(e => {
    dropArea.addEventListener(e, ev => { ev.preventDefault(); dropArea.classList.remove('dragover'); });
  });
  dropArea.addEventListener('drop', ev => {
    fileInput.files = ev.dataTransfer.files;
    const names = Array.from(ev.dataTransfer.files).map(f => f.name).join(', ');
    display.textContent = names ? '✓ ' + names : '';
  });

  {% if column_section %}
    document.getElementById('cleaning').scrollIntoView({ behavior: 'smooth', block: 'start' });
  {% endif %}

