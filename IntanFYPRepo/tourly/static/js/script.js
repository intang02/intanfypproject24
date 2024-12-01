'use strict';

/**
 * navbar toggle
 */

const overlay = document.querySelector("[data-overlay]");
const navOpenBtn = document.querySelector("[data-nav-open-btn]");
const navbar = document.querySelector("[data-navbar]");
const navCloseBtn = document.querySelector("[data-nav-close-btn]");
const navLinks = document.querySelectorAll("[data-nav-link]");

const navElemArr = [navOpenBtn, navCloseBtn, overlay];

const navToggleEvent = function (elem) {
  for (let i = 0; i < elem.length; i++) {
    elem[i].addEventListener("click", function () {
      navbar.classList.toggle("active");
      overlay.classList.toggle("active");
    });
  }
}

navToggleEvent(navElemArr);
navToggleEvent(navLinks);



/**
 * header sticky & go to top
 */

const header = document.querySelector("[data-header]");
const goTopBtn = document.querySelector("[data-go-top]");

window.addEventListener("scroll", function () {

  if (window.scrollY >= 200) {
    header.classList.add("active");
    goTopBtn.classList.add("active");
  } else {
    header.classList.remove("active");
    goTopBtn.classList.remove("active");
  }

});

//date range picker
document.addEventListener('DOMContentLoaded', function() {
  const searchForm = document.getElementById('searchForm');
  const datePicker = flatpickr("#datePicker", {
    mode: "range",
    minDate: "today",
    showMonths: 2,
    disableMobile: true,
    locale: {
      firstDayOfWeek: 1
    },
    onChange: function(selectedDates) {
      if (selectedDates.length === 2) {
        const checkinDate = new Date(selectedDates[0]);
        const checkoutDate = new Date(selectedDates[1]);

        // Adjust dates to UTC to avoid time zone issues
        const formattedCheckinDate = checkinDate.toLocaleDateString('en-CA'); // YYYY-MM-DD format
        const formattedCheckoutDate = checkoutDate.toLocaleDateString('en-CA'); // YYYY-MM-DD format


        console.log("Formatted Check-in Date:", formattedCheckinDate);
        console.log("Formatted Check-out Date:", formattedCheckoutDate);

        // Set hidden fields
        document.getElementById('checkin_date').value = formattedCheckinDate;
        document.getElementById('checkout_date').value = formattedCheckoutDate;
      }
    }
  });

  searchForm.addEventListener('submit', function(event) {
    event.preventDefault(); // Stop default form submission

    const selectedDates = datePicker.selectedDates;
    if (selectedDates.length === 2) {
      const checkinDate = new Date(selectedDates[0]);
      const checkoutDate = new Date(selectedDates[1]);

      // Adjust dates to UTC to avoid time zone issues
      const formattedCheckinDate = checkinDate.toLocaleDateString('en-CA'); // YYYY-MM-DD format
      const formattedCheckoutDate = checkoutDate.toLocaleDateString('en-CA'); // YYYY-MM-DD format


      console.log("Submitting Check-in Date:", formattedCheckinDate);
      console.log("Submitting Check-out Date:", formattedCheckoutDate);

      // Create hidden inputs if they don't already exist
      let checkinInput = document.querySelector('input[name="checkin_date"]');
      if (!checkinInput) {
        checkinInput = document.createElement('input');
        checkinInput.type = 'hidden';
        checkinInput.name = 'checkin_date';
        searchForm.appendChild(checkinInput);
      }
      checkinInput.value = formattedCheckinDate;

      let checkoutInput = document.querySelector('input[name="checkout_date"]');
      if (!checkoutInput) {
        checkoutInput = document.createElement('input');
        checkoutInput.type = 'hidden';
        checkoutInput.name = 'checkout_date';
        searchForm.appendChild(checkoutInput);
      }
      checkoutInput.value = formattedCheckoutDate;

      // Submit the form
      searchForm.submit();
    } else {
      alert("Please select a valid date range.");
    }
  });
});







//num of pax
// Show pax container when pax input is clicked
document.getElementById('pax-input').addEventListener('click', function(event) {
  event.stopPropagation(); // Prevent the click event from propagating to document
  
  const paxContainer = document.querySelector('.pax-container');
  const paxInput = document.getElementById('pax-input');
  
  // Get the bounding box of the pax input
  const inputRect = paxInput.getBoundingClientRect();
  
  // Calculate the space below and above the input
  const spaceBelow = window.innerHeight - inputRect.bottom;
  const spaceAbove = inputRect.top;
  
  // Set the dropdown position based on available space
  if (spaceBelow < paxContainer.offsetHeight && spaceAbove > paxContainer.offsetHeight) {
    // If there is not enough space below but enough space above, position the dropdown above the input
    paxContainer.style.top = 'auto';
    paxContainer.style.bottom = `${inputRect.height}px`; // Position it right above the input
  } else {
    // Otherwise, position it below
    paxContainer.style.top = `${inputRect.height}px`; // Position it right below the input
    paxContainer.style.bottom = 'auto';
  }

  paxContainer.style.display = 'block';
});

// Increase and decrease room count
document.getElementById('room-increase').addEventListener('click', function() {
  let roomInput = document.getElementById('rooms');
  roomInput.value = parseInt(roomInput.value) + 1;
});

document.getElementById('room-decrease').addEventListener('click', function() {
  let roomInput = document.getElementById('rooms');
  if (roomInput.value > 1) {
    roomInput.value = parseInt(roomInput.value) - 1;
  }
});

// Hide pax container and update the input when 'Done' button is clicked
document.getElementById('done-button').addEventListener('click', function() {
  const adults = document.getElementById('adults').value;
  const rooms = document.getElementById('rooms').value;
  document.getElementById('pax-input').value = `${adults} adults, ${rooms} rooms`;
  document.querySelector('.pax-container').style.display = 'none';
});


// Increase and decrease adult count
document.getElementById('adult-increase').addEventListener('click', function() {
  let adultInput = document.getElementById('adults');
  adultInput.value = parseInt(adultInput.value) + 1;
});

document.getElementById('adult-decrease').addEventListener('click', function() {
  let adultInput = document.getElementById('adults');
  if (adultInput.value > 1) {
      adultInput.value = parseInt(adultInput.value) - 1;
  }
});



// Hide pax container when clicking outside of it
document.addEventListener('click', function(event) {
  const paxContainer = document.querySelector('.pax-container');
  const paxInput = document.getElementById('pax-input');

  if (!paxContainer.contains(event.target) && event.target !== paxInput) {
    paxContainer.style.display = 'none';
  }
});




/*budget range picker */
document.addEventListener("DOMContentLoaded", function () {
  const budgetInput = document.getElementById("budgetInput");
  const budgetPickerContainer = document.getElementById("budgetPickerContainer");
  const budgetRange = document.getElementById("budgetRange");
  const budgetValue = document.getElementById("budgetValue");

  // Toggle the visibility of the budget picker
  budgetInput.addEventListener("click", function () {
    if (budgetPickerContainer.style.display === "none" || budgetPickerContainer.style.display === "") {
      budgetPickerContainer.style.display = "flex"; // Show picker
    } else {
      budgetPickerContainer.style.display = "none"; // Hide picker
    }
  });

  // Update the value as the user moves the slider
  budgetRange.addEventListener("input", function () {
    const formattedValue = "RM " + new Intl.NumberFormat().format(budgetRange.value);
    budgetValue.textContent = formattedValue;
    budgetInput.value = formattedValue; // Update the input box value in real-time
  });

  // Update the input box when the user clicks outside of the picker
  document.addEventListener("click", function (event) {
    if (!budgetInput.contains(event.target) && !budgetPickerContainer.contains(event.target)) {
      budgetPickerContainer.style.display = "none"; // Hide picker
    }
  });
});



//Managing or Limiting Multiple Submissions on Client-Side

document.addEventListener('DOMContentLoaded', function() {
  var submitButton = document.getElementById('searchButton');
  var form = document.getElementById('searchForm');
  
  submitButton.addEventListener('click', debounce(function(event) {
      form.submit();
  }, 300)); // Adjust the time (ms) according to your requirement
});

function debounce(func, wait, immediate) {
  var timeout;
  return function() {
      var context = this, args = arguments;
      var later = function() {
          timeout = null;
          if (!immediate) func.apply(context, args);
      };
      var callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func.apply(context, args);
  };
}


document.addEventListener("DOMContentLoaded", function() {
  const spinner = document.getElementById("spinner");
  if (spinner) {
    spinner.style.display = 'block';
  }
});




