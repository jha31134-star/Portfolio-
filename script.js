// Theme toggle (remembers the choice in the browser)
const root = document.documentElement;
const themeBtn = document.getElementById('themeBtn');

function setTheme(theme) {
  root.setAttribute('data-theme', theme);
  themeBtn.textContent = theme === 'dark' ? 'Light' : 'Dark';
  try { localStorage.setItem('theme', theme); } catch (e) { /* storage unavailable */ }
}

let saved = null;
try { saved = localStorage.getItem('theme'); } catch (e) { /* ignore */ }
setTheme(saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
themeBtn.addEventListener('click', () => {
  setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
});

// Mobile menu
const menuBtn = document.getElementById('menuBtn');
const navLinks = document.getElementById('navLinks');
menuBtn.addEventListener('click', () => {
  const open = navLinks.classList.toggle('open');
  menuBtn.setAttribute('aria-expanded', open);
});
navLinks.addEventListener('click', (e) => {
  if (e.target.tagName === 'A') {
    navLinks.classList.remove('open');
    menuBtn.setAttribute('aria-expanded', false);
  }
});

// Project filter (only exists on projects.html; querySelectorAll is safe when empty)
document.querySelectorAll('.chip').forEach((chip) => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach((c) => c.classList.remove('active'));
    chip.classList.add('active');
    const filter = chip.dataset.filter;
    document.querySelectorAll('.project').forEach((p) => {
      p.classList.toggle('hidden', filter !== 'all' && p.dataset.type !== filter);
    });
  });
});

// Contact form opens the visitor's email app (only exists on contact.html)
const contactForm = document.getElementById('contactForm');
if (contactForm) {
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    const subject = encodeURIComponent('Portfolio message from ' + data.get('name'));
    const body = encodeURIComponent(data.get('message'));
    window.location.href = 'mailto:jha31134@gmail.com?subject=' + subject + '&body=' + body;
  });
}

// Footer year
document.getElementById('year').textContent = new Date().getFullYear();
