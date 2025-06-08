function spin(slug) {
  const modal = document.getElementById('wheelModal');
  const canvas = document.getElementById('wheel');
  const overlay = document.querySelector('.tap-overlay');
  const ctx = canvas.getContext('2d');
  
  // Show modal
  modal.style.display = 'flex';
  
  // Set canvas size based on container
  const container = canvas.parentElement;
  const size = Math.min(container.offsetWidth - 40, container.offsetHeight - 40);
  canvas.width = size;
  canvas.height = size;
  
  // Wheel properties
  const centerX = size / 2;
  const centerY = size / 2;
  const radius = size * 0.45;
  const slices = 12;
  const sliceAngle = (2 * Math.PI) / slices;
  
  // Colors from CSS variables
  const winColor = '#3ddfb2'; // var(--mint)
  const loseColor = '#ff5f87'; // var(--rose)
  const inkColor = '#1e1b55'; // var(--ink)
  const sunColor = '#ffce3d'; // var(--sun)
  
  let currentRotation = 0;
  let isSpinning = false;
  
  // Function to draw the wheel at a specific rotation
  function drawWheel(rotation) {
    ctx.clearRect(0, 0, size, size);
    
    // Save the context state
    ctx.save();
    
    // Move to center and rotate
    ctx.translate(centerX, centerY);
    ctx.rotate(rotation);
    ctx.translate(-centerX, -centerY);
    
    // Draw the wheel segments
    for (let i = 0; i < slices; i++) {
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, i * sliceAngle - Math.PI/2, (i + 1) * sliceAngle - Math.PI/2);
      ctx.closePath();
      ctx.fillStyle = i % 2 === 0 ? winColor : loseColor;
      ctx.fill();
      ctx.strokeStyle = inkColor;
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Add WIN/LOSE text
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(i * sliceAngle + sliceAngle/2 - Math.PI/2);
      ctx.textAlign = 'center';
      ctx.font = 'bold 20px Poppins';
      ctx.fillStyle = inkColor;
      ctx.fillText(i % 2 === 0 ? 'WIN' : 'LOSE', radius * 0.7, 7);
      ctx.restore();
    }
    
    // Restore context before drawing center circle
    ctx.restore();
    
    // Draw center circle (not rotated)
    ctx.beginPath();
    ctx.arc(centerX, centerY, size * 0.08, 0, 2 * Math.PI);
    ctx.fillStyle = inkColor;
    ctx.fill();
    ctx.strokeStyle = sunColor;
    ctx.lineWidth = 3;
    ctx.stroke();
  }
  
  // Draw initial wheel
  drawWheel(0);
  
  // Click/touch handler - attach to overlay instead of canvas
  function handleSpin(e) {
    e.preventDefault(); // Prevent any default touch behavior
    
    if (isSpinning) return;
    isSpinning = true;
    
    overlay.style.display = 'none';
    
    // Add spinning class to modal content for CSS effects
    const modalContent = document.querySelector('.modal-content');
    modalContent.classList.add('spinning');
    
    // Make the API call first to determine the result
    fetch('/spin/' + slug, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(data => {
      // Calculate rotation to land on the predetermined result
      const isWin = data.result === 'WIN';
      const fullRotations = 5 + Math.floor(Math.random() * 3); // 5-7 full rotations
      
      // Find a slice of the correct type (win or lose)
      const targetSlices = [];
      for (let i = 0; i < slices; i++) {
        if ((i % 2 === 0) === isWin) {
          targetSlices.push(i);
        }
      }
      
      // Pick a random target slice of the correct type
      const targetSlice = targetSlices[Math.floor(Math.random() * targetSlices.length)];
      const sliceStart = targetSlice * 30; // 360/12 = 30 degrees per slice
      const sliceOffset = Math.random() * 20 + 5; // Land somewhere in the middle of the slice
      const finalAngle = -sliceStart - sliceOffset;      
      const totalRotation = fullRotations * 360 + finalAngle;
      const duration = 4000 + Math.random() * 2000; // 4-6 seconds in milliseconds
      const startTime = Date.now();
      const startRotation = currentRotation;
      
      // Easing function for smooth deceleration
      function easeOut(t) {
        return 1 - Math.pow(1 - t, 3);
      }
      
      // Animation loop with shake effect
      function animate() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = easeOut(progress);
        
        // Calculate rotation
        currentRotation = startRotation + (totalRotation * Math.PI / 180) * easedProgress;
        
        // Clear the entire canvas including any transform effects
        ctx.clearRect(0, 0, size, size);
        
        // Save context state
        ctx.save();
        
        // Add shake effect that decreases over time
        const shakeIntensity = (1 - easedProgress) * 3; // Starts at 3px, reduces to 0
        const shakeX = (Math.random() - 0.5) * shakeIntensity;
        const shakeY = (Math.random() - 0.5) * shakeIntensity;
        
        // Apply shake transform
        ctx.translate(shakeX, shakeY);
        
        // Draw the wheel with current rotation
        drawWheel(currentRotation);
        
        // Restore context
        ctx.restore();
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          // Final draw without shake
          drawWheel(currentRotation);
          
          // Remove spinning class
          const modalContent = document.querySelector('.modal-content');
          modalContent.classList.remove('spinning');
          
          // Animation complete, redirect
          setTimeout(() => {
            window.location.href = `/result/${slug}`;
          }, 500);
        }
      }
      
      animate();
    })
    .catch(error => {
      console.error('Spin error:', error);
      modal.style.display = 'none';
      isSpinning = false;
      overlay.style.display = 'flex';
      // Remove spinning class on error
      const modalContent = document.querySelector('.modal-content');
      modalContent.classList.remove('spinning');
    });
  }
  
  // Attach handlers to both overlay and canvas
  overlay.onclick = handleSpin;
  overlay.ontouchstart = handleSpin;
  canvas.onclick = handleSpin;
  canvas.ontouchstart = handleSpin;
  
  // Also handle modal background clicks to close
  modal.onclick = function(e) {
    if (e.target === modal && !isSpinning) {
      modal.style.display = 'none';
    }
  };
}