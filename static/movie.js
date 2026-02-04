// const movies = {
//   mov1: {
//     title: "Frieren: Beyond Journey’s End",
//     desc: "Second season of Frieren. The adventure is over, but life goes on.",
//     img: "Images/Frieren.jpg"
//   },
//   mov2: {
//     title: "Hell's Paradise Season 2",
//     desc: "Gabimaru returns in a brutal fight for survival.",
//     img: "Images/HellParadise.jpg"
//   },
//   mov3: {
//     title: "Jujutsu Kaisen: Culling Game",
//     desc: "Deadly battles begin after the Shibuya incident.",
//     img: "Images/JujutsuKaisen.jpg"
//   }
// };
// const params = new URLSearchParams(window.location.search);
// const movieId = params.get("id");

// const movie = movies[movieId];

// const params = new URLSearchParams(window.location.search);
// const movieId = params.get("movie_id");

 // Generate 4x6 seat matrix
    const seatMatrix = document.getElementById('seatMatrix');
    for (let i = 1; i <= 4; i++) {
      for (let j = 1; j <= 6; j++) {
        const seat = document.createElement('div');
        seat.classList.add('seat');
        seat.dataset.row = i;
        seat.dataset.col = j;
        seat.innerText = `${i},${j}`;
        
        // Click to toggle seat selection
        seat.addEventListener('click', () => {
          seat.classList.toggle('selected');
        });

        seatMatrix.appendChild(seat);
      }
    }

    function bookTicket() {
      const selectedSeats = [...document.querySelectorAll('.seat.selected')]
        .map(seat => `${seat.dataset.row},${seat.dataset.col}`);
      if (selectedSeats.length > 0) {
        alert(`You booked seats: ${selectedSeats.join(' | ')}`);
      } else {
        alert("No seats selected!");
      }
    }