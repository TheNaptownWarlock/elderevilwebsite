document.addEventListener('DOMContentLoaded', () => {
    const audioPlayer = new Audio();
    const playPauseBtn = document.getElementById('playPause');
    const prevTrackBtn = document.getElementById('prevTrack');
    const nextTrackBtn = document.getElementById('nextTrack');
    const progressBar = document.getElementById('progressBar');
    const progressContainer = document.querySelector('.progress-container');
    const trackTitle = document.getElementById('trackTitle');

    let currentTrackIndex = 0;
    let isPlaying = false;
    
    // Define tracks directly
    const tracks = [
        {
            title: 'Bio Electric Piano',
            path: 'assets/audio/Music/BioElectricPiano.mp3'
        }
    ];

    function loadTrack(index) {
        if (tracks.length === 0) return;
        
        audioPlayer.src = tracks[index].path;
        trackTitle.textContent = tracks[index].title;
        audioPlayer.load();
        
        // Add error handling
        audioPlayer.onerror = function() {
            console.error('Error loading audio file:', tracks[index].path);
            trackTitle.textContent = 'Error loading track';
        };
    }

    function playPause() {
        if (tracks.length === 0) return;
        
        if (isPlaying) {
            audioPlayer.pause();
            playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
        } else {
            audioPlayer.play()
                .then(() => {
                    playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
                    isPlaying = true;
                })
                .catch(error => {
                    console.error('Error playing audio:', error);
                    trackTitle.textContent = 'Error playing track';
                });
        }
    }

    function nextTrack() {
        if (tracks.length === 0) return;
        
        currentTrackIndex = (currentTrackIndex + 1) % tracks.length;
        loadTrack(currentTrackIndex);
        if (isPlaying) {
            audioPlayer.play();
        }
    }

    function prevTrack() {
        if (tracks.length === 0) return;
        
        currentTrackIndex = (currentTrackIndex - 1 + tracks.length) % tracks.length;
        loadTrack(currentTrackIndex);
        if (isPlaying) {
            audioPlayer.play();
        }
    }

    function updateProgress() {
        const progress = (audioPlayer.currentTime / audioPlayer.duration) * 100;
        progressBar.style.width = `${progress}%`;
    }

    function setProgress(e) {
        const width = this.clientWidth;
        const clickX = e.offsetX;
        const duration = audioPlayer.duration;
        audioPlayer.currentTime = (clickX / width) * duration;
    }

    // Load the first track
    loadTrack(currentTrackIndex);

    // Event Listeners
    playPauseBtn.addEventListener('click', playPause);
    nextTrackBtn.addEventListener('click', nextTrack);
    prevTrackBtn.addEventListener('click', prevTrack);
    audioPlayer.addEventListener('timeupdate', updateProgress);
    progressContainer.addEventListener('click', setProgress);
    audioPlayer.addEventListener('ended', nextTrack);
}); 