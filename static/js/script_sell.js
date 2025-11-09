document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('sellForm');
    const previewBtn = document.getElementById('previewBtn');
    const submitBtn = document.getElementById('submitBtn');
    const previewContainer = document.getElementById('product-details');
    const previewContent = document.getElementById('productDisplay');
    const productSelect = document.getElementById('product');
    const otherProductDiv = document.getElementById('otherProductDiv');
    const otherProductInput = document.getElementById('otherProduct');

    // Show/hide "Other Product" input field
    productSelect.addEventListener('change', () => {
        if (productSelect.value === 'Other') {
            otherProductDiv.style.display = 'block';
            otherProductInput.required = true;
        } else {
            otherProductDiv.style.display = 'none';
            otherProductInput.required = false;
        }
    });

    // Handle preview button click
    previewBtn.addEventListener('click', () => {
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const product = productSelect.value === 'Other' ? otherProductInput.value.trim() : productSelect.value;
        const price = document.getElementById('price').value.trim();
        const description = document.getElementById('description').value.trim();
        const primaryImage = document.getElementById('primaryImage').files[0];
        const additionalImages = document.getElementById('additionalImages').files;

        // Validate required fields
        if (!name || !email || !phone || !product || !price || !description || !primaryImage) {
            alert("Please fill all required fields before previewing.");
            return;
        }

        // Read and display primary image
        const reader = new FileReader();
        reader.onload = function (event) {
            previewContent.innerHTML = `
                <h3>Preview Your Submission</h3>
                <p><strong>Seller Name:</strong> ${name}</p>
                <p><strong>Email Address:</strong> ${email}</p>
                <p><strong>Phone Number:</strong> ${phone}</p>
                <p><strong>Product Name:</strong> ${product}</p>
                <p><strong>Price:</strong> ₹${price}</p>
                <p><strong>Description:</strong> ${description}</p>
                <p><strong>Primary Image:</strong></p>
                <img src="${event.target.result}" alt="Primary Image" style="max-width: 100%; margin: 10px 0;">
                <div id="additionalImagesPreview"></div>
            `;

            // Handle additional images
            const additionalPreviewContainer = document.getElementById('additionalImagesPreview');

            if (additionalImages.length > 0) {
                additionalPreviewContainer.innerHTML = '<p><strong>Additional Images:</strong></p>';
                let imgPromises = [];

                Array.from(additionalImages).forEach((file) => {
                    let imgReader = new FileReader();
                    let promise = new Promise((resolve) => {
                        imgReader.onload = function (imgEvent) {
                            let img = document.createElement('img');
                            img.src = imgEvent.target.result;
                            img.alt = "Additional Image";
                            img.style = "max-width: 100px; margin: 5px;";
                            additionalPreviewContainer.appendChild(img);
                            resolve();
                        };
                    });

                    imgReader.readAsDataURL(file);
                    imgPromises.push(promise);
                });

                // Ensure all images are loaded before displaying preview
                Promise.all(imgPromises).then(() => {
                    previewContainer.style.display = 'block';
                    submitBtn.style.display = 'block';
                });
            } else {
                previewContainer.style.display = 'block';
                submitBtn.style.display = 'block';
            }
        };

        reader.readAsDataURL(primaryImage);
    });
});
