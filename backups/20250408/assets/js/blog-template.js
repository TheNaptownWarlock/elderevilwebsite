document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('blogTemplateForm');
    const previewButton = document.getElementById('previewButton');
    const generateButton = document.getElementById('generateButton');
    const previewArea = document.getElementById('previewArea');
    const imageInput = document.getElementById('postImage');
    const imagePreview = document.getElementById('imagePreview');

    // Handle image preview
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
            }
            reader.readAsDataURL(file);
        }
    });

    // Preview button functionality
    previewButton.addEventListener('click', function() {
        const title = document.getElementById('postTitle').value;
        const date = document.getElementById('postDate').value;
        const content = document.getElementById('postContent').value;
        const imageFile = imageInput.files[0];

        if (!title || !date || !content) {
            alert('Please fill in all required fields');
            return;
        }

        // Format date
        const formattedDate = new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        // Create preview HTML
        let previewHTML = `
            <h1>${title}</h1>
            <p class="blog-date">${formattedDate}</p>
            <div class="blog-content">
                ${content.split('\n').map(paragraph => `<p>${paragraph}</p>`).join('')}
        `;

        if (imageFile) {
            previewHTML += `<img src="${URL.createObjectURL(imageFile)}" alt="${title}" style="max-width: 100%; margin: 1rem 0;">`;
        }

        previewHTML += `
            </div>
            <a href="index.html#blog" class="glow-button">Back to Blog</a>
        `;

        previewArea.innerHTML = previewHTML;
        previewArea.style.display = 'block';
    });

    // Function to update index.html with new blog post preview
    async function updateIndexHtml(title, date, content, folderName) {
        try {
            // Instead of fetching, we'll create the updated HTML directly
            const newPost = document.createElement('article');
            newPost.className = 'blog-post';
            
            // Get first paragraph for preview - handle content safely
            let previewText = '';
            if (typeof content === 'string') {
                // Split by newlines and get the first non-empty line
                const paragraphs = content.split('\n').filter(line => line.trim() !== '');
                previewText = paragraphs.length > 0 ? paragraphs[0] : content.substring(0, 200) + '...';
            } else {
                previewText = 'Read the full post...';
            }
            
            // Format the date
            const formattedDate = new Date(date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            newPost.innerHTML = `
                <h3>${title}</h3>
                <p class="blog-date">${formattedDate}</p>
                <p>${previewText}</p>
                <a href="blog-posts/${folderName}/" class="read-more">Read More</a>
            `;
            
            // Create the complete HTML structure
            const updatedHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Naptown Warlock</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Germania+One&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <header class="glow-effect">
            <nav>
                <ul>
                    <li><a href="#home">Home</a></li>
                    <li><a href="#food">Elder Cuisine</a></li>
                    <li><a href="#clay">The Lil Guys</a></li>
                    <li><a href="#blog">Blog</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </nav>
        </header>

        <main>
            <section id="home" class="hero-section">
                <h1 class="glow-text">The Naptown Warlock</h1>
                <p class="subtitle">Culinary Magic & Creative Crafts</p>
                <div class="social-links">
                    <a href="https://www.instagram.com/TheNaptownWarlock" target="_blank" class="social-icon">
                        <i class="fab fa-instagram"></i>
                    </a>
                </div>
            </section>

            <section id="food" class="portfolio-section">
                <h2>Elder Cuisine</h2>
                <div class="portfolio-grid">
                    <div class="portfolio-item">
                        <div class="slideshow-container" id="elder-evil-coffee-slideshow">
                            <div class="slide">
                                <img src="assets/images/food/Elder Evil Coffee/Sidama Roast 4_6_25/IMG_6607.jpg" alt="Sidama Roast Coffee">
                                <div class="slide-description">
                                    <p class="image-date">2024</p>
                                    <p>First roast in awhile for my friends over at Bucket O' Blood! From the mountains of Sidama in Ethiopia. Turbinado flavor comes across quite well.</p>
                                </div>
                            </div>
                            <button class="prev-btn" aria-label="Previous image">❮</button>
                            <button class="next-btn" aria-label="Next image">❯</button>
                        </div>
                        <div class="project-icon">
                            <i class="fas fa-coffee"></i>
                        </div>
                        <h3>Elder Evil Coffee</h3>
                        <p class="project-description"><em>I started all my creative endeavors wondering what I was capable of. That started with sourcing and roasting coffee beans.</em></p>
                    </div>
                    <div class="portfolio-item">
                        <div class="slideshow-container" id="necro-nom-icon-slideshow">
                            <div class="slide">
                                <img src="assets/images/food/Necro-NOM-icon/cinnamon rolls.jpg" alt="Cursed Cinnamon Rolls">
                                <div class="slide-description">
                                    <p class="image-date">2024</p>
                                    <p>Where death meets deliciousness. Our Necro-NOM-icon creations bring new life to classic recipes, transforming them into something truly extraordinary. From cursed cinnamon rolls to bewitched empanadas, each bite tells a story of culinary resurrection.</p>
                                </div>
                            </div>
                            <div class="slide">
                                <img src="assets/images/food/Necro-NOM-icon/Goatcheeseanddateempanada.jpg" alt="Bewitched Empanadas">
                                <div class="slide-description">
                                    <p class="image-date">2024</p>
                                    <p>Where death meets deliciousness. Our Necro-NOM-icon creations bring new life to classic recipes, transforming them into something truly extraordinary. From cursed cinnamon rolls to bewitched empanadas, each bite tells a story of culinary resurrection.</p>
                                </div>
                            </div>
                            <button class="prev-btn" aria-label="Previous image">❮</button>
                            <button class="next-btn" aria-label="Next image">❯</button>
                        </div>
                        <div class="project-icon">
                            <i class="fas fa-utensils"></i>
                        </div>
                        <h3>Necro-NOM-icon</h3>
                        <p class="project-description"><em>This is a general repository of my cooking projects.</em></p>
                    </div>
                    <div class="portfolio-item">
                        <div class="slideshow-container" id="elder-cow-slideshow">
                            <div class="slide">
                                <img src="assets/images/food/The Elder Cow/Jade for Ellis/IMG_6638.jpg" alt="Jade Cheese">
                                <div class="slide-description">
                                    <p class="image-date">2024</p>
                                    <p>Ellis was my old roommate for a couple years! After recently hanging out she gave me a bunch of tea she had imported recently. I used my techniques from Water Lilies here and was able to successfully infuse the flavor in and make a great texture. So much so that me and other friends killed two pints pretty quickly. Will be more deliberate in these texture techniques going forward!</p>
                                </div>
                            </div>
                            <div class="slide">
                                <img src="assets/images/food/The Elder Cow/Outlaw Country for Chad/IMG_6219.jpg" alt="Outlaw Country Cheese">
                                <div class="slide-description">
                                    <p class="image-date">2024</p>
                                    <p>For my next project I wanted to do something really unhinged for my chaotic friend Chad. We joke about beans alot so I wondered if I could make a baked bean ice cream. Chad is really into old western films so I themed it around that. I decided to see if I could smoke the milk and it worked! Then candied bacon and added it with baked beans to the churn. Very divisive. Some folks were reviled by the bean texture other weren't too fond of the smoke flavor. I actually thought the smoke flavor worked well but the main issue here was I had added bourbon which raised the freezing point making the base texture not as good as normal. Should've been softer. Still got alot of laughs out of this one.</p>
                                </div>
                            </div>
                            <div class="slide">
                                <img src="assets/images/food/The Elder Cow/Water Lilies for Illya/IMG_6096.jpg" alt="Water Lilies Cheese">
                                <div class="slide-description">
                                    <p class="image-date">2024</p>
                                    <p>This was the first project in my ice cream series. I wanted to do it for my dear friend Illya as he is always pushing me to challenge myself with projects. Illya and I used to work at the Art Institute together so I wanted to theme it around that. Since he had given me some Parisian tea, I decided to theme it after Monet's Water Lilies. I torched cinnamon bark and let it sit in the milk with some of the tea to infuse it. Then made lemon cake that I added during the churn. The lemon cake was like the yellow lilies arising from the water and the base had a nice cereal milk flavor quality.</p>
                                </div>
                            </div>
                            <button class="prev-btn" aria-label="Previous image">❮</button>
                            <button class="next-btn" aria-label="Next image">❯</button>
                        </div>
                        <div class="project-icon">
                            <i class="fas fa-ice-cream"></i>
                        </div>
                        <h3>The Elder Cow</h3>
                        <p class="project-description"><em>I started this project as way to deal with late night anxiety spikes. I try to make a themed ice cream for friends once a week.</em></p>
                    </div>
                </div>
            </section>

            <section id="clay" class="portfolio-section">
                <h2>The Lil Guys</h2>
                <div class="portfolio-grid">
                    <div class="portfolio-item">
                        <div class="slideshow-container" id="jester-slideshow">
                            <div class="slide">
                                <img src="assets/images/clay/Lil Guy 1 - The Jester/IMG_6603.jpg" alt="The Jester - Front View">
                                <div class="slide-description">
                                    <p class="image-date">2024</p>
                                    <p>A soft lad who always brings a laugh.</p>
                                </div>
                            </div>
                            <div class="slide">
                                <img src="assets/images/clay/Lil Guy 1 - The Jester/IMG_6424.jpg" alt="The Jester - Detail View">
                                <div class="slide-description">
                                    <p class="image-date">2024</p>
                                    <p>A soft lad who always brings a laugh.</p>
                                </div>
                            </div>
                            <button class="prev-btn" aria-label="Previous image">❮</button>
                            <button class="next-btn" aria-label="Next image">❯</button>
                        </div>
                        <h3>The Jester</h3>
                        <p>A soft lad who always brings a laugh.</p>
                    </div>
                    <div class="portfolio-item">
                        <div class="slideshow-container" id="wizard-slideshow">
                            <div class="slide">
                                <img src="assets/images/clay/Lil Guy 2 - The Wizard/IMG_6749.jpg" alt="The Wizard - Front View">
                                <div class="slide-description">
                                    <p class="image-date">2024</p>
                                    <p>A prestigious master of magicks, unfortunately he still hasn't mastered his potion tolerance.</p>
                                </div>
                            </div>
                            <div class="slide">
                                <img src="assets/images/clay/Lil Guy 2 - The Wizard/IMG_6606.jpg" alt="The Wizard - Detail View">
                                <div class="slide-description">
                                    <p class="image-date">2024</p>
                                    <p>A prestigious master of magicks, unfortunately he still hasn't mastered his potion tolerance.</p>
                                </div>
                            </div>
                            <button class="prev-btn" aria-label="Previous image">❮</button>
                            <button class="next-btn" aria-label="Next image">❯</button>
                        </div>
                        <h3>The Wizard</h3>
                        <p>A prestigious master of magicks, unfortunately he still hasn't mastered his potion tolerance.</p>
                    </div>
                </div>
            </section>

            <section id="blog" class="blog-section">
                <h2>Blog</h2>
                <div class="blog-posts">
                    ${newPost.outerHTML}
                </div>
            </section>

            <section id="about" class="about-section">
                <h2>About</h2>
                <div class="about-content">
                    <p>Welcome to my mystical corner of creativity! I'm The Naptown Warlock, a culinary artist and craftsperson exploring the intersection of food, art, and the mysterious. From eldritch feasts to dark clay creations, I blend traditional techniques with a touch of the arcane.</p>
                </div>
            </section>

            <section id="contact" class="contact-section">
                <h2>Contact</h2>
                <form class="contact-form" action="https://formspree.io/f/xpwpogbv" method="POST">
                    <input type="text" name="name" placeholder="Name" required>
                    <input type="email" name="email" placeholder="Email" required>
                    <textarea name="message" placeholder="Message" required></textarea>
                    <button type="submit" class="glow-button">Send Message</button>
                </form>
            </section>

            <section id="chat" class="chat-section">
                <h2>Chat Room</h2>
                <div class="chat-container">
                    <div id="chat-messages" class="chat-messages"></div>
                    <form id="chat-form" class="chat-form">
                        <input type="text" id="message-input" placeholder="Type your message..." required>
                        <button type="submit" class="glow-button">Send</button>
                    </form>
                </div>
            </section>
        </main>

        <footer class="glow-effect">
            <div class="social-links">
                <a href="https://www.instagram.com/TheNaptownWarlock" target="_blank" class="social-icon">
                    <i class="fab fa-instagram"></i>
                </a>
            </div>
            <p>&copy; 2024 The Naptown Warlock. All rights reserved.</p>
        </footer>
    </div>

    // Image Popup
    <div id="image-popup" class="image-popup">
        <button class="close-popup">&times;</button>
        <img class="popup-image" src="" alt="">
        <div class="popup-description"></div>
    </div>

    <script src="assets/js/slideshow.js"></script>
    <script src="assets/js/chat.js"></script>

    // Get the current page title
    const pageTitle = document.querySelector('h1').textContent;
    
    // Update the document title
    document.title = `${pageTitle} - The Naptown Warlock`;

    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add glow effect to navigation links on hover
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.textShadow = '0 0 10px var(--glow-color)';
        });
        link.addEventListener('mouseleave', function() {
            this.style.textShadow = 'none';
        });
    });
}); 