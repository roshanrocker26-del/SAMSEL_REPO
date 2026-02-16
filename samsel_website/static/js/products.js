// ===== SERIES + BOOK STACK (SCROLL ONLY WHEN CURSOR IS INSIDE BOOK AREA) =====

let currentSeries = 0;   // 0 = IBOT, 1 = ISMART
let currentSlide = 0;
let isAnimating = false;

const seriesSections = document.querySelectorAll('.series-section');

function getElements(section) {
  return {
    books: section.querySelectorAll('.book'),
    index: section.querySelectorAll('.index'),
    content: section.querySelectorAll('.content')
  };
}

function showSlide(section, i) {
  const { books, index, content } = getElements(section);

  books.forEach(el => el.classList.remove('active'));
  index.forEach(el => el.classList.remove('active'));
  content.forEach(el => el.classList.remove('active'));

  if (books[i]) books[i].classList.add('active');
  if (index[i]) index[i].classList.add('active');
  if (content[i]) content[i].classList.add('active');
}


// ===== CHECK IF CURSOR IS INSIDE THE BOOK LAYOUT =====
function isInsideBooksArea(e) {
  const activeSection = seriesSections[currentSeries];
  const layout = activeSection.querySelector('.series-layout');

  if (!layout) return false;

  const rect = layout.getBoundingClientRect();

  return (
    e.clientX >= rect.left &&
    e.clientX <= rect.right &&
    e.clientY >= rect.top &&
    e.clientY <= rect.bottom
  );
}


// ===== SCROLL → CHANGE BOOKS ONLY WHEN INSIDE BOOK AREA =====
window.addEventListener('wheel', (e) => {

  // If NOT inside books → allow normal page scroll
  if (!isInsideBooksArea(e)) return;

  // Stop page scroll ONLY when interacting with books
  e.preventDefault();

  if (isAnimating) return;

  const activeSection = seriesSections[currentSeries];
  const { books } = getElements(activeSection);

  if (e.deltaY > 0) {
    currentSlide = Math.min(currentSlide + 1, books.length - 1);
  } else {
    currentSlide = Math.max(currentSlide - 1, 0);
  }

  showSlide(activeSection, currentSlide);

  isAnimating = true;
  setTimeout(() => isAnimating = false, 650);

}, { passive: false });


// ===== BUTTONS → SWITCH SERIES ONLY =====
function goSeries(dir) {
  const newSeries = currentSeries + dir;

  if (newSeries < 0 || newSeries >= seriesSections.length) return;

  // hide current
  seriesSections[currentSeries].classList.remove('active-series');

  // switch
  currentSeries = newSeries;
  currentSlide = 0;

  // show new
  seriesSections[currentSeries].classList.add('active-series');

  showSlide(seriesSections[currentSeries], currentSlide);
}


// ===== INITIAL LOAD =====
seriesSections[0].classList.add('active-series');
showSlide(seriesSections[0], 0);

function showPurchase(type){

  const whatsapp = document.getElementById("whatsapp-box");
  const email = document.getElementById("email-box");
  const buttons = document.querySelectorAll(".toggle-btn");

  buttons.forEach(btn => btn.classList.remove("active"));

  if(type === "whatsapp"){
    whatsapp.classList.add("active");
    email.classList.remove("active");
    buttons[0].classList.add("active");
  }else{
    email.classList.add("active");
    whatsapp.classList.remove("active");
    buttons[1].classList.add("active");
  }
}
