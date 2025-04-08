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
            // Fetch the current index.html from the root directory
            const response = await fetch('../index.html');
            const html = await response.text();
            
            // Create a temporary div to parse the HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Find the blog section and blog posts container
            const blogSection = doc.querySelector('#blog');
            const blogPostsContainer = blogSection.querySelector('.blog-posts');
            
            if (!blogSection || !blogPostsContainer) {
                throw new Error('Blog section or posts container not found in index.html');
            }
            
            // Create the new blog post preview
            const newPost = doc.createElement('article');
            newPost.className = 'blog-post';
            
            // Get first paragraph for preview
            const firstParagraph = content.split('\n')[0];
            
            // Format the date
            const formattedDate = new Date(date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            newPost.innerHTML = `
                <h3>${title}</h3>
                <p class="blog-date">${formattedDate}</p>
                <p>${firstParagraph}</p>
                <a href="blog-posts/${folderName}/" class="read-more">Read More</a>
            `;
            
            // Insert the new post at the beginning of the blog posts container
            blogPostsContainer.insertBefore(newPost, blogPostsContainer.firstChild);
            
            // Convert the updated document back to HTML
            const updatedHtml = doc.documentElement.outerHTML;
            
            // Create a download link for the updated index.html
            const blob = new Blob([updatedHtml], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'index.html';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            return true;
        } catch (error) {
            console.error('Error updating index.html:', error);
            return false;
        }
    }

    // Update the generate button click handler
    generateButton.addEventListener('click', async function() {
        const title = document.getElementById('postTitle').value;
        const date = document.getElementById('postDate').value;
        const content = document.getElementById('postContent').value;
        const imageFile = imageInput.files[0];

        if (!title || !date || !content) {
            alert('Please fill in all required fields');
            return;
        }

        // Create a sanitized folder name from the title
        const folderName = title.toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)/g, '');

        // Format date
        const formattedDate = new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        // Create the blog post HTML
        let blogPostHTML = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title} - The Naptown Warlock</title>
    <link rel="stylesheet" href="../../styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Germania+One&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <header class="glow-effect">
            <nav>
                <ul>
                    <li><a href="../../index.html#home">Home</a></li>
                    <li><a href="../../index.html#food">Elder Cuisine</a></li>
                    <li><a href="../../index.html#clay">The Lil Guys</a></li>
                    <li><a href="../../index.html#blog">Blog</a></li>
                    <li><a href="../../index.html#about">About</a></li>
                    <li><a href="../../index.html#contact">Contact</a></li>
                </ul>
            </nav>
        </header>

        <main>
            <article class="blog-post-full">
                <h1>${title}</h1>
                <p class="blog-date">${formattedDate}</p>
                <div class="blog-content">
                    ${content.split('\n').map(paragraph => `<p>${paragraph}</p>`).join('')}
        `;

        if (imageFile) {
            // Create a unique filename for the image
            const imageFilename = `blog-${Date.now()}-${imageFile.name}`;
            blogPostHTML += `<img src="images/${imageFilename}" alt="${title}" style="max-width: 100%; margin: 1rem 0;">`;
        }

        blogPostHTML += `
                </div>
                <a href="../../index.html#blog" class="glow-button">Back to Blog</a>
            </article>
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
</body>
</html>`;

        // Create a zip file containing the blog post structure
        const zip = new JSZip();
        
        // Add the HTML file
        zip.file(`${folderName}/index.html`, blogPostHTML);
        
        // Create images folder and add image if present
        if (imageFile) {
            const imagesFolder = zip.folder(`${folderName}/images`);
            imagesFolder.file(imageFile.name, imageFile);
        }

        // Generate the zip file
        zip.generateAsync({type: "blob"})
            .then(async function(content) {
                // Create a download link for the zip file
                const url = URL.createObjectURL(content);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${folderName}.zip`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);

                // Update index.html
                const success = await updateIndexHtml(title, date, content, folderName);
                
                if (success) {
                    alert('Blog post generated! Please:\n' +
                          `1. Extract ${folderName}.zip to the blog-posts directory\n` +
                          '2. Replace the existing index.html with the downloaded one\n' +
                          '3. The structure will be: blog-posts/' + folderName + '/index.html and images/');
                } else {
                    alert('Blog post generated, but there was an error updating index.html.\n' +
                          'Please manually update index.html with the new blog post preview.');
                }
            });
    });
}); 