document.getElementById("timespanType").addEventListener("change", function () {
    const inputBox = document.getElementById("timespanInput");
    inputBox.style.display = this.value === "none" ? "none" : "block";
    inputBox.placeholder = `Enter ${this.value}`;
});
const inputField = document.getElementById("groupMembers");
const dropdownList = document.getElementById("dropdownList");
const selectedMembersContainer = document.getElementById("selectedMembers");
const hiddenGroupMembers = document.getElementById("hiddenGroupMembers");

const editIcon = document.getElementById("editIcon");
const groupForm = document.getElementById("groupForm");
const chatPlaceholder = document.getElementById("chatPlaceholder") || document.getElementById("chatContainer");
const closeGroupForm = document.getElementById("closeGroupForm");
const groupProfilePicInput = document.getElementById("groupProfilePic");
const groupPicPreview = document.getElementById("groupPicPreview");
const createGroupBtn = document.getElementById("createGroupBtn");

let selectedMembers = [];

function selectPerson(element) {
    const name = element.textContent.trim();

    if (!selectedMembers.includes(name)) {
        selectedMembers.push(name);
        updateSelectedMembers();
    }

    inputField.value = "";
    dropdownList.style.display = "none";
}

function updateSelectedMembers() {
    selectedMembersContainer.innerHTML = "";

    if (selectedMembers.length > 0) {
        selectedMembersContainer.style.display = "flex"; // Show box
    } else {
        selectedMembersContainer.style.display = "none"; // Hide when empty
    }

    
    selectedMembers.forEach(name => {
        const memberTag = document.createElement("div");
        memberTag.classList.add("member-tag");
        memberTag.innerHTML = `${name} <span class="remove-btn" onclick="removeMember('${name}')">×</span>`;
        
        selectedMembersContainer.appendChild(memberTag);
    });

    // Update hidden input value
    hiddenGroupMembers.value = selectedMembers.join(",");

    // Auto-scroll to right
    selectedMembersContainer.scrollLeft = selectedMembersContainer.scrollWidth;
}

function removeMember(name) {
    selectedMembers = selectedMembers.filter(member => member !== name);
    updateSelectedMembers();
}

inputField.addEventListener("input", () => {
    const searchTerm = inputField.value.toLowerCase();
    let found = false;

    document.querySelectorAll(".dropdown-list li").forEach(item => {
        if (item.textContent.toLowerCase().includes(searchTerm)) {
            item.style.display = "block";
            found = true;
        } else {
            item.style.display = "none";
        }
    });

    dropdownList.style.display = found ? "block" : "none";
});

document.addEventListener("click", (event) => {
    if (!event.target.closest(".dropdown-container")) {
        dropdownList.style.display = "none";
    }
});


    // 📌 Toggle Group Form (Works for both templates)
    if (editIcon && groupForm && chatPlaceholder) {
        editIcon.addEventListener("click", function () {
            if (groupForm.style.display === "block") {
                groupForm.style.display = "none"; // Hide group form
                chatPlaceholder.style.display = "flex"; // Show placeholder/chat-container
            } else {
                groupForm.style.display = "block"; // Show group form
                chatPlaceholder.style.display = "none"; // Hide placeholder/chat-container
            }
        });

        closeGroupForm.addEventListener("click", function () {
            groupForm.style.display = "none";
            chatPlaceholder.style.display = "flex"; // Restore chatPlaceholder/chatContainer visibility
        });
    }

    // 📌 Handle Group Profile Picture Upload & Preview
groupProfilePicInput.addEventListener("change", function (event) {
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            groupPicPreview.src = e.target.result;
            groupImageURL = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

