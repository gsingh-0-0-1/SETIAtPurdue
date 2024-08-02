// script.js

document.addEventListener("DOMContentLoaded", function() {
    const imageContainer = document.getElementById("image-container");
    const submitButton = document.getElementById("submit-button");

    // Function to fetch images from the backend server
    async function fetchImages() {
        try {
            const response = await fetch('/api/training/1/images');
            const images = await response.json();
            populateImages(images);
        } catch (error) {
            console.error('Error fetching images:', error);
        }
    }

    // Function to populate the page with images and dropdowns
    function populateImages(images) {
        images.forEach((image, index) => {
            const imageItem = document.createElement('div');
            imageItem.classList.add('image-item');

            const imgElement = document.createElement('img');
            imgElement.src = image.url;
            imgElement.alt = `Image ${index + 1}`;

            const dropdown = document.createElement('select');
            dropdown.classList.add('dropdown');
            dropdown.setAttribute('data-image-id', image.id);

            const optionNoise = document.createElement('option');
            optionNoise.value = 'noise';
            optionNoise.textContent = 'Noise';

            const optionRfi = document.createElement('option');
            optionRfi.value = 'rfi';
            optionRfi.textContent = 'RFI';

            const optionCandidate = document.createElement('option');
            optionCandidate.value = 'candidate';
            optionCandidate.textContent = 'Candidate';

            dropdown.appendChild(optionNoise);
            dropdown.appendChild(optionRfi);
            dropdown.appendChild(optionCandidate);

            imageItem.appendChild(imgElement);
            imageItem.appendChild(dropdown);
            imageContainer.appendChild(imageItem);
        });
    }

    // Function to collect the user's choices and submit to the server
    async function submitChoices() {
        const dropdowns = document.querySelectorAll('.dropdown');
        const choices = Array.from(dropdowns).map(dropdown => ({
            imageId: dropdown.getAttribute('data-image-id'),
            classification: dropdown.value
        }));

        try {
            const response = await fetch('/api/training/1/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ choices })
            });

            if (response.ok) {
                alert('Choices submitted successfully!');
            } else {
                alert('Error submitting choices.');
            }
        } catch (error) {
            console.error('Error submitting choices:', error);
        }
    }

    submitButton.addEventListener('click', submitChoices);

    // Fetch images when the page loads
    fetchImages();
});

