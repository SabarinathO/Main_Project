document.addEventListener("DOMContentLoaded", function () {
    let userId = Number(document.getElementById("userId").dataset.userid);
    const groupId = document.getElementById("groupId").dataset.groupid;
    let chatMessages = document.getElementById("chatMessages");

    // Establish WebSocket connection
    const chatSocket = new WebSocket(`ws://${window.location.host}/ws/groupchat/${groupId}/`);

    chatSocket.onmessage = function (e) {
        let data = JSON.parse(e.data);
        let senderName = data.sender_name || "Unknown";

        // Create new message div
        let newMessage = document.createElement("div");
        newMessage.classList.add("message", data.sender_id == userId ? "sent-message" : "received-message");

        // Format timestamp to local time
        let timestamp = data.timestamp ? formatTimestamp(data.timestamp) : "";

        newMessage.innerHTML = `
            <span class="sender-name">${senderName}</span>
            <span class="message-text">${data.message}</span>
            <span class="message-time">${timestamp}</span>
        `;

        chatMessages.appendChild(newMessage);

        // Auto-scroll to the latest message
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Send message function
    function sendMessage() {
        let inputField = document.getElementById("messageInput");
        let message = inputField.value.trim();
        if (message !== "") {
            chatSocket.send(JSON.stringify({
                "message": message,
                "sender_id": userId
            }));
            inputField.value = "";
        }
    }

    // Send message on Enter key press
    document.getElementById("messageInput").addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    // Auto-scroll on page load
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Convert timestamp properly to 12-hour format in local time
    function formatTimestamp(timestamp) {
        let date = new Date(timestamp);
        let now = new Date();

        let hours = date.getHours();
        let minutes = date.getMinutes();
        let ampm = hours >= 12 ? "PM" : "AM";
        hours = hours % 12 || 12; // Convert 0 to 12
        minutes = minutes < 10 ? "0" + minutes : minutes;

        // Check if the message is from yesterday or earlier
        let isPreviousDay = date.toDateString() !== now.toDateString();

        return isPreviousDay
            ? `${date.toDateString()} ${hours}:${minutes} ${ampm}` // Show date + time for older messages
            : `${hours}:${minutes} ${ampm}`; // Show only time for today's messages
    }

      // Group Info Box Functionality
      const groupBox = document.getElementById("groupBox");
      const showGroupBox = document.getElementById("showGroupBox");
  
      if (groupBox && showGroupBox) {
          // Show group box when clicking "Tap here for group info"
          showGroupBox.addEventListener("click", function (event) {
              groupBox.style.display = "block";
              event.stopPropagation(); // Prevent immediate closing
          });
  
          // Hide group box when clicking outside
          document.addEventListener("click", function (event) {
              if (!groupBox.contains(event.target) && event.target !== showGroupBox) {
                  groupBox.style.display = "none";
              }
          });
      }
  });