/**
 * TOO MUCH, YET NEVER ENOUGH — DIGITAL READER APPLICATION
 * Literary reader logic, 3D book opening animation, signature integration, and back cover.
 */

(function () {
  'use strict';

  // --- State Variables ---
  let bookData = null;
  let flatChapters = []; // List of all chapters with metadata
  let currentChapterIndex = 0;
  let currentThemeIndex = 0;
  const themes = ['cream', 'sepia', 'dark'];
  let currentFontSize = 1.125; // rem base

  // --- DOM Elements ---
  const views = {
    home: document.getElementById('view-home'),
    reader: document.getElementById('view-reader')
  };

  const book3D = document.getElementById('book-3d');
  const btnBegin = document.getElementById('btn-begin');
  const btnResume = document.getElementById('btn-resume');
  const btnViewBackCover = document.getElementById('btn-view-back-cover');

  const modalBackCover = document.getElementById('modal-back-cover');
  const btnCloseBackCover = document.getElementById('btn-close-back-cover');
  const backdropBackCover = document.getElementById('backdrop-back-cover');

  const btnHome = document.getElementById('btn-home');
  const btnTheme = document.getElementById('btn-theme');
  const btnFontDec = document.getElementById('btn-font-dec');
  const btnFontInc = document.getElementById('btn-font-inc');
  const btnToc = document.getElementById('btn-toc');
  const btnTocFooter = document.getElementById('btn-toc-footer');
  const btnTocBackCover = document.getElementById('btn-toc-back-cover');
  const btnCloseToc = document.getElementById('btn-close-toc');

  const readerMain = document.getElementById('reader-main');
  const progressBar = document.getElementById('progress-bar');
  const chapterIndicator = document.getElementById('current-chapter-indicator');

  const partBanner = document.getElementById('part-banner');
  const partBannerNum = document.getElementById('part-banner-num');
  const partBannerTitle = document.getElementById('part-banner-title');

  const chNumber = document.getElementById('ch-number');
  const chTitle = document.getElementById('ch-title');
  const chBody = document.getElementById('ch-body');
  const epilogueSignature = document.getElementById('epilogue-signature');

  const btnPrevCh = document.getElementById('btn-prev-ch');
  const btnNextCh = document.getElementById('btn-next-ch');
  const prevChTitle = document.getElementById('prev-ch-title');
  const nextChTitle = document.getElementById('next-ch-title');
  const bookFooter = document.getElementById('book-footer');

  const tocOverlay = document.getElementById('toc-overlay');
  const tocBackdrop = document.getElementById('toc-backdrop');
  const tocList = document.getElementById('toc-list');

  // --- Initialization ---
  async function init() {
    // Load book data
    if (window.BOOK_DATA) {
      bookData = window.BOOK_DATA;
    } else {
      try {
        const resp = await fetch('data/book.json');
        bookData = await resp.json();
      } catch (err) {
        console.error('Failed to load book data:', err);
        return;
      }
    }

    buildFlatChapters();
    buildTableOfContents();
    loadSavedState();
    setupEventListeners();

    if (localStorage.getItem('zeyra_book_last_ch')) {
      btnResume.classList.remove('hidden');
    }
  }

  // --- Build Flat Chapters List ---
  function buildFlatChapters() {
    flatChapters = [];
    bookData.parts.forEach(part => {
      part.chapters.forEach(ch => {
        flatChapters.push({
          ...ch,
          part_number: part.part_number,
          part_title: part.part_title,
          part_id: part.id
        });
      });
    });
  }

  // --- Build TOC Overlay Drawer ---
  function buildTableOfContents() {
    tocList.innerHTML = '';

    bookData.parts.forEach(part => {
      const groupDiv = document.createElement('div');
      groupDiv.className = 'toc-part-group';

      const partHdr = document.createElement('div');
      partHdr.className = 'toc-part-header';
      partHdr.innerHTML = `${part.part_number} <span class="toc-part-title-sub">${part.part_title}</span>`;
      groupDiv.appendChild(partHdr);

      part.chapters.forEach(ch => {
        const link = document.createElement('a');
        link.className = 'toc-item-link';
        link.href = `#${ch.id}`;
        link.dataset.id = ch.id;

        const labelSpan = document.createElement('span');
        labelSpan.textContent = ch.full_title;
        link.appendChild(labelSpan);

        link.addEventListener('click', (e) => {
          e.preventDefault();
          const idx = flatChapters.findIndex(c => c.id === ch.id);
          if (idx !== -1) {
            currentChapterIndex = idx;
            renderChapter(currentChapterIndex);
            switchView('reader');
            closeToc();
          }
        });

        groupDiv.appendChild(link);
      });

      tocList.appendChild(groupDiv);
    });
  }

  // --- Trigger 3D Book Opening Experience ---
  function triggerBookOpening(targetChapterIndex = 0) {
    book3D.classList.add('is-opening');
    setTimeout(() => {
      renderChapter(targetChapterIndex);
      switchView('reader');
      book3D.classList.remove('is-opening');
    }, 700);
  }

  // --- Render Chapter Content ---
  function renderChapter(index) {
    if (index < 0 || index >= flatChapters.length) return;

    const ch = flatChapters[index];
    currentChapterIndex = index;

    // Save Progress
    localStorage.setItem('zeyra_book_last_ch', ch.id);

    // Update Header Indicator
    chapterIndicator.textContent = ch.chapter_number;

    // Part Banner Logic
    const prevCh = flatChapters[index - 1];
    const isNewPart = !prevCh || prevCh.part_id !== ch.part_id;

    if (isNewPart) {
      partBannerNum.textContent = ch.part_number;
      partBannerTitle.textContent = ch.part_title;
      partBanner.classList.remove('hidden');
    } else {
      partBanner.classList.add('hidden');
    }

    // Set Chapter Header
    chNumber.textContent = ch.chapter_number;
    chTitle.textContent = ch.title;

    // Render Body Text Paragraphs
    chBody.innerHTML = '';
    ch.content.forEach(line => {
      const p = document.createElement('p');
      p.textContent = line;
      chBody.appendChild(p);
    });

    // Epilogue Signature
    if (ch.id === 'epilogue') {
      epilogueSignature.classList.remove('hidden');
    } else {
      epilogueSignature.classList.add('hidden');
    }

    // Prev / Next Navigation Buttons
    if (index > 0) {
      btnPrevCh.disabled = false;
      prevChTitle.textContent = flatChapters[index - 1].title;
    } else {
      btnPrevCh.disabled = true;
      prevChTitle.textContent = '---';
    }

    if (index < flatChapters.length - 1) {
      btnNextCh.disabled = false;
      nextChTitle.textContent = flatChapters[index + 1].title;
      bookFooter.classList.add('hidden');
    } else {
      btnNextCh.disabled = true;
      nextChTitle.textContent = 'End of Book';
      bookFooter.classList.remove('hidden');
    }

    // Highlight Active TOC Item
    document.querySelectorAll('.toc-item-link').forEach(link => {
      link.classList.toggle('active', link.dataset.id === ch.id);
    });

    // Scroll reader to top
    window.scrollTo(0, 0);
    readerMain.focus();

    updateProgressBar();
  }

  // --- View Switcher ---
  function switchView(viewName) {
    if (viewName === 'home') {
      views.home.classList.remove('hidden');
      views.reader.classList.add('hidden');
      progressBar.style.width = '0%';
    } else if (viewName === 'reader') {
      views.home.classList.add('hidden');
      views.reader.classList.remove('hidden');
      updateProgressBar();
    }
  }

  // --- Progress Bar ---
  function updateProgressBar() {
    if (views.reader.classList.contains('hidden') || flatChapters.length === 0) return;
    const progress = ((currentChapterIndex + 1) / flatChapters.length) * 100;
    progressBar.style.width = `${progress}%`;
  }

  // --- Theme Toggle ---
  function cycleTheme() {
    currentThemeIndex = (currentThemeIndex + 1) % themes.length;
    applyTheme(themes[currentThemeIndex]);
  }

  function applyTheme(themeName) {
    document.body.className = `theme-${themeName}`;
    localStorage.setItem('zeyra_book_theme', themeName);
  }

  // --- Font Size Adjustment ---
  function adjustFontSize(delta) {
    currentFontSize = Math.min(Math.max(currentFontSize + delta, 0.9), 1.5);
    document.body.style.fontSize = `${currentFontSize}rem`;
    localStorage.setItem('zeyra_book_fontsize', currentFontSize);
  }

  // --- Modal & TOC Controls ---
  function openToc() {
    tocOverlay.classList.remove('hidden');
    tocOverlay.setAttribute('aria-hidden', 'false');
    const activeItem = tocList.querySelector('.toc-item-link.active');
    if (activeItem) {
      activeItem.scrollIntoView({ block: 'center' });
    }
  }

  function closeToc() {
    tocOverlay.classList.add('hidden');
    tocOverlay.setAttribute('aria-hidden', 'true');
  }

  function openBackCoverModal() {
    modalBackCover.classList.remove('hidden');
    modalBackCover.setAttribute('aria-hidden', 'false');
  }

  function closeBackCoverModal() {
    modalBackCover.classList.add('hidden');
    modalBackCover.setAttribute('aria-hidden', 'true');
  }

  // --- Load Persistence ---
  function loadSavedState() {
    const savedTheme = localStorage.getItem('zeyra_book_theme');
    if (savedTheme && themes.includes(savedTheme)) {
      currentThemeIndex = themes.indexOf(savedTheme);
      applyTheme(savedTheme);
    }

    const savedFontSize = localStorage.getItem('zeyra_book_fontsize');
    if (savedFontSize) {
      currentFontSize = parseFloat(savedFontSize);
      document.body.style.fontSize = `${currentFontSize}rem`;
    }
  }

  // --- Event Listeners Setup ---
  function setupEventListeners() {
    // 3D Book & Homepage Actions
    book3D.addEventListener('click', () => triggerBookOpening(0));
    btnBegin.addEventListener('click', () => triggerBookOpening(0));

    btnResume.addEventListener('click', () => {
      const lastChId = localStorage.getItem('zeyra_book_last_ch');
      const idx = flatChapters.findIndex(c => c.id === lastChId);
      triggerBookOpening(idx !== -1 ? idx : 0);
    });

    btnViewBackCover.addEventListener('click', openBackCoverModal);
    btnCloseBackCover.addEventListener('click', closeBackCoverModal);
    backdropBackCover.addEventListener('click', closeBackCoverModal);

    btnHome.addEventListener('click', () => {
      switchView('home');
    });

    // Controls
    btnTheme.addEventListener('click', cycleTheme);
    btnFontDec.addEventListener('click', () => adjustFontSize(-0.075));
    btnFontInc.addEventListener('click', () => adjustFontSize(0.075));

    // TOC Triggers
    btnToc.addEventListener('click', openToc);
    btnTocFooter.addEventListener('click', openToc);
    btnTocBackCover.addEventListener('click', () => {
      closeToc();
      openBackCoverModal();
    });
    btnCloseToc.addEventListener('click', closeToc);
    tocBackdrop.addEventListener('click', closeToc);

    // Prev / Next Chapter Buttons
    btnPrevCh.addEventListener('click', () => {
      if (currentChapterIndex > 0) {
        renderChapter(currentChapterIndex - 1);
      }
    });

    btnNextCh.addEventListener('click', () => {
      if (currentChapterIndex < flatChapters.length - 1) {
        renderChapter(currentChapterIndex + 1);
      }
    });

    // Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
      if (!modalBackCover.classList.contains('hidden')) {
        if (e.key === 'Escape') closeBackCoverModal();
        return;
      }

      if (!tocOverlay.classList.contains('hidden')) {
        if (e.key === 'Escape') closeToc();
        return;
      }

      if (views.reader.classList.contains('hidden')) return;

      if (e.key === 'ArrowLeft') {
        if (currentChapterIndex > 0) renderChapter(currentChapterIndex - 1);
      } else if (e.key === 'ArrowRight') {
        if (currentChapterIndex < flatChapters.length - 1) renderChapter(currentChapterIndex + 1);
      } else if (e.key.toLowerCase() === 'm') {
        openToc();
      }
    });

    // Scroll listener for top progress bar
    window.addEventListener('scroll', () => {
      if (views.reader.classList.contains('hidden')) return;
      const totalScroll = document.documentElement.scrollHeight - window.innerHeight;
      if (totalScroll > 0) {
        const pageRatio = window.scrollY / totalScroll;
        const baseProgress = (currentChapterIndex / flatChapters.length) * 100;
        const stepProgress = (1 / flatChapters.length) * 100 * pageRatio;
        progressBar.style.width = `${Math.min(baseProgress + stepProgress, 100)}%`;
      }
    });
  }

  // Run app initialization on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
