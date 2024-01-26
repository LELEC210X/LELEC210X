// Get template
const source = document.getElementById("body_source").innerHTML;
const template = Handlebars.compile(source);

// Get destination
const destination = document.getElementsByTagName("body")[0];

// Init websocket

// Uncomment this on the server
/*
const socket = io("wss://perceval.elen.ucl.ac.be", {
  path: "/lelec210x/socket.io",
});
*/

// Command this on the server
const socket = io();

const scrollAmount = 100;
const lapScrollStart = 4;

let scrollDiff = 0;

// Populate leaderboard callback
socket.on("update_leaderboard", (message) => {
  // Retrieve state from local storage if it exists
  let state = JSON.parse(sessionStorage.getItem("state"));
  if (state === null) {
    state = {
      client: null,
      currentScrollValue: 0,
      lastScrollValue: 0,
      doubleLastScrollValue: 0,
    };
  }

  if (
    state.client != null &&
    message.current_lap != null &&
    message.current_lap > lapScrollStart
  ) {
    scrollDiff = message.current_lap - state.client.current_lap;
  }

  let resetScroll = message.current_lap == 0;
  state.client = message;
  if (resetScroll) {
    state.doubleLastScrollValue = 0;
    state.lastScrollValue = 0;
    state.currentScrollValue = 0;
  }

  // Update HTML with new values
  let compiledHtml = template({
    round_name: state.client.round_name,
    current_round: state.client.current_round + 1,
    current_lap: state.client.current_lap + 1,
    number_of_rounds: state.client.number_of_rounds,
    number_of_laps: state.client.number_of_laps,
    paused: state.client.paused,
    time_before_next_lap: state.client.time_before_next_lap.toFixed(1),
    laps: Array.from({ length: state.client.number_of_laps }, (_, i) => i + 1),
    leaderboard: state.client.leaderboard,
  });
  destination.innerHTML = compiledHtml;

  // Update scrollElem /!\ recompiling the template resets the scroll position
  let scrollElem = document.getElementById("leaderboard_wrapper");
  scrollElem.scrollBy({
    top: 0,
    left: state.currentScrollValue,
    behavior: "instant",
  });

  // Scroll into view
  if (scrollDiff > 0) {
    let totalScrollAmount = scrollDiff * scrollAmount;
    state.doubleLastScrollValue = state.lastScrollValue;
    state.lastScrollValue = scrollElem.scrollLeft;
    if (
      state.doubleLastScrollValue > 0 &&
      state.doubleLastScrollValue == state.lastScrollValue
    ) {
      scrollElem.scrollBy({
        top: 0,
        left: scrollElem.scrollWidth * -1,
        behavior: "smooth",
      });
    } else {
      scrollElem.scrollBy({
        top: 0,
        left: totalScrollAmount,
        behavior: "smooth",
      });
    }
    state.currentScrollValue = state.lastScrollValue + totalScrollAmount;
  }

  // Save state
  sessionStorage.setItem("state", JSON.stringify(state));
});
