// Prediction page specific JavaScript functionality

document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("fileInput")
  const fileUploadArea = document.getElementById("fileUploadArea")
  const fileInfo = document.getElementById("fileInfo")
  const fileName = document.getElementById("fileName")
  const removeFileBtn = document.getElementById("removeFile")
  const analyzeBtn = document.getElementById("analyzeBtn")
  const uploadForm = document.getElementById("uploadForm")
  const progressContainer = document.getElementById("progressContainer")
  const progressFill = document.getElementById("progressFill")
  const progressText = document.getElementById("progressText")

  let selectedFile = null

  // File upload area click handler
  if (fileUploadArea) {
    fileUploadArea.addEventListener("click", (e) => {
      if (e.target !== removeFileBtn && !e.target.closest(".remove-file")) {
        fileInput.click()
      }
    })
  }

  // File input change handler
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0]
      if (file) {
        handleFileSelection(file)
      }
    })
  }

  // Drag and drop functionality
  if (fileUploadArea) {
    fileUploadArea.addEventListener("dragover", (e) => {
      e.preventDefault()
      fileUploadArea.classList.add("dragover")
    })

    fileUploadArea.addEventListener("dragleave", (e) => {
      e.preventDefault()
      if (!fileUploadArea.contains(e.relatedTarget)) {
        fileUploadArea.classList.remove("dragover")
      }
    })

    fileUploadArea.addEventListener("drop", (e) => {
      e.preventDefault()
      fileUploadArea.classList.remove("dragover")

      const files = e.dataTransfer.files
      if (files.length > 0) {
        const file = files[0]
        handleFileSelection(file)
      }
    })
  }

  // Remove file button handler
  if (removeFileBtn) {
    removeFileBtn.addEventListener("click", (e) => {
      e.stopPropagation()
      clearFileSelection()
    })
  }

  // Form submission handler
  if (uploadForm) {
    uploadForm.addEventListener("submit", (e) => {
      e.preventDefault()

      if (!selectedFile) {
        showNotification("Please select a medical image file first.", "error")
        return
      }

      if (!validateFile(selectedFile)) {
        return
      }

      submitForm()
    })
  }

  // Sample image click handlers
  const sampleItems = document.querySelectorAll(".sample-item")
  sampleItems.forEach((item) => {
    item.addEventListener("click", function () {
      const condition = this.getAttribute("data-condition")
      showSampleAnalysis(condition)
    })
  })

  function handleFileSelection(file) {
    if (!validateFile(file)) {
      return
    }

    selectedFile = file
    updateFileInfo(file)

    if (fileInfo) {
      fileInfo.style.display = "flex"
    }

    enableAnalysisButton()

    // Hide the upload prompt
    const uploadIcon = fileUploadArea.querySelector(".upload-icon")
    const uploadText = fileUploadArea.querySelector("h3")
    const uploadSubtext = fileUploadArea.querySelector("p")

    if (uploadIcon) uploadIcon.style.display = "none"
    if (uploadText) uploadText.style.display = "none"
    if (uploadSubtext) uploadSubtext.style.display = "none"

    // Show file preview if it's an image
    if (file.type.startsWith("image/")) {
      showImagePreview(file)
    }

    showNotification("Medical image selected successfully", "success")
  }

  function validateFile(file) {
    // Check file type
    const allowedTypes = ["image/jpeg", "image/jpg", "image/png"]
    const allowedExtensions = [".jpg", ".jpeg", ".png", ".dicom"]

    const isValidType = allowedTypes.includes(file.type)
    const isValidExtension = allowedExtensions.some((ext) => file.name.toLowerCase().endsWith(ext))

    if (!isValidType && !isValidExtension) {
      showNotification("Please select a valid medical image file (JPEG, PNG, or DICOM)", "error")
      return false
    }

    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024 // 10MB in bytes
    if (file.size > maxSize) {
      showNotification("File size must be less than 10MB", "error")
      return false
    }

    // Check minimum file size
    const minSize = 1024 // 1KB
    if (file.size < minSize) {
      showNotification("File appears to be corrupted or too small", "error")
      return false
    }

    return true
  }

  function showImagePreview(file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      // Remove existing preview
      const existingPreview = fileUploadArea.querySelector(".file-preview")
      if (existingPreview) {
        existingPreview.remove()
      }

      // Create preview
      const preview = document.createElement("div")
      preview.className = "file-preview"
      preview.innerHTML = `
        <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 150px; border-radius: 8px; margin-top: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
      `

      fileUploadArea.appendChild(preview)
    }
    reader.readAsDataURL(file)
  }

  function submitForm() {
    const formData = new FormData()
    formData.append("file", selectedFile)

    // Show loading state
    setLoadingState(analyzeBtn, true)
    if (progressContainer) {
      progressContainer.style.display = "block"
    }

    // Simulate progress for better UX
    let progress = 0
    const progressInterval = setInterval(() => {
      progress += Math.random() * 15
      if (progress > 90) progress = 90

      if (progressFill) {
        progressFill.style.width = progress + "%"
      }
      if (progressText) {
        if (progress < 30) {
          progressText.textContent = "Uploading medical image..."
        } else if (progress < 60) {
          progressText.textContent = "Preprocessing image data..."
        } else if (progress < 90) {
          progressText.textContent = "Running AI analysis..."
        } else {
          progressText.textContent = "Generating results..."
        }
      }
    }, 200)

    // Submit the form
    fetch("/predict", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        clearInterval(progressInterval)
        if (progressFill) progressFill.style.width = "100%"
        if (progressText) progressText.textContent = "Analysis complete!"

        if (response.ok) {
          return response.text()
        } else {
          throw new Error("Analysis failed")
        }
      })
      .then((html) => {
        // If the response is HTML (redirect to results), navigate to it
        setTimeout(() => {
          document.open()
          document.write(html)
          document.close()
        }, 500)
      })
      .catch((error) => {
        console.error("Error:", error)
        clearInterval(progressInterval)
        setLoadingState(analyzeBtn, false)
        if (progressContainer) {
          progressContainer.style.display = "none"
        }
        showNotification("Error analyzing medical image. Please try again.", "error")
      })
  }

  function showSampleAnalysis(condition) {
    // Create sample analysis data
    const sampleData = {
      normal: {
        prediction: "Normal",
        confidence: 87.5,
        description: "Healthy kidney tissue with no detectable abnormalities",
        urgency: "None",
      },
      cyst: {
        prediction: "Cyst",
        confidence: 91.2,
        description: "Fluid-filled sac detected in kidney tissue",
        urgency: "Low",
      },
      stone: {
        prediction: "Stone",
        confidence: 89.8,
        description: "Mineral deposits detected in kidney structure",
        urgency: "Medium",
      },
      tumor: {
        prediction: "Tumor",
        confidence: 85.3,
        description: "Abnormal tissue growth detected requiring immediate attention",
        urgency: "High",
      },
    }

    const data = sampleData[condition]
    if (data) {
      // Show loading state
      setLoadingState(analyzeBtn, true)
      showNotification(`Analyzing sample ${condition} image...`, "info")

      // Simulate analysis time
      setTimeout(() => {
        // Create a form to submit sample data
        const form = document.createElement("form")
        form.method = "POST"
        form.action = "/predict"
        form.style.display = "none"

        // Add sample data as hidden inputs
        Object.keys(data).forEach((key) => {
          const input = document.createElement("input")
          input.type = "hidden"
          input.name = key
          input.value = data[key]
          form.appendChild(input)
        })

        // Add sample flag
        const sampleInput = document.createElement("input")
        sampleInput.type = "hidden"
        sampleInput.name = "sample"
        sampleInput.value = "true"
        form.appendChild(sampleInput)

        document.body.appendChild(form)
        form.submit()
      }, 1500)
    }
  }

  // File size display helper
  function formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  // Update file info display
  function updateFileInfo(file) {
    const fileSize = formatFileSize(file.size)
    const fileType = file.type.split("/")[1]?.toUpperCase() || "Unknown"

    if (fileName) {
      fileName.innerHTML = `
        <div>
          <strong>${file.name}</strong>
          <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">
            ${fileType} • ${fileSize}
          </div>
        </div>
      `
    }
  }

  // Keyboard accessibility
  document.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      if (e.target === fileUploadArea) {
        e.preventDefault()
        fileInput.click()
      }
    }
  })

  // Add ARIA attributes for accessibility
  if (fileUploadArea) {
    fileUploadArea.setAttribute("role", "button")
    fileUploadArea.setAttribute("tabindex", "0")
    fileUploadArea.setAttribute("aria-label", "Click to upload medical image or drag and drop")
  }

  function clearFileSelection() {
    selectedFile = null
    if (fileInput) fileInput.value = ""

    if (fileInfo) {
      fileInfo.style.display = "none"
    }

    // Show the upload prompt again
    const uploadIcon = fileUploadArea.querySelector(".upload-icon")
    const uploadText = fileUploadArea.querySelector("h3")
    const uploadSubtext = fileUploadArea.querySelector("p")

    if (uploadIcon) uploadIcon.style.display = "block"
    if (uploadText) uploadText.style.display = "block"
    if (uploadSubtext) uploadSubtext.style.display = "block"

    disableAnalysisButton()

    // Remove any preview
    const existingPreview = fileUploadArea.querySelector(".file-preview")
    if (existingPreview) {
      existingPreview.remove()
    }

    showNotification("File selection cleared", "info")
  }

  function enableAnalysisButton() {
    if (analyzeBtn) {
      analyzeBtn.disabled = false
      analyzeBtn.classList.remove("btn-disabled")
    }
  }

  function disableAnalysisButton() {
    if (analyzeBtn) {
      analyzeBtn.disabled = true
      analyzeBtn.classList.add("btn-disabled")
    }
  }

  // File validation on page load
  if (fileInput && fileInput.files.length > 0) {
    handleFileSelection(fileInput.files[0])
  }

  // Initialize drag and drop visual feedback
  document.addEventListener("dragover", (e) => {
    e.preventDefault()
  })

  document.addEventListener("drop", (e) => {
    e.preventDefault()
  })

  // Add paste functionality for images
  document.addEventListener("paste", (e) => {
    const items = e.clipboardData?.items
    if (items) {
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf("image") !== -1) {
          const file = items[i].getAsFile()
          if (file) {
            handleFileSelection(file)
            showNotification("Image pasted successfully", "success")
          }
          break
        }
      }
    }
  })

  console.log("Medical image prediction interface initialized")
})

// Notification function declaration
function showNotification(message, type) {
  const notification = document.createElement("div")
  notification.classList.add("notification", type)
  notification.textContent = message
  document.body.appendChild(notification)

  setTimeout(() => {
    document.body.removeChild(notification)
  }, 5000)
}

// Loading state function declaration
function setLoadingState(button, isLoading) {
  if (button) {
    button.disabled = isLoading
    if (isLoading) {
      button.classList.add("btn-loading")
    } else {
      button.classList.remove("btn-loading")
    }
  }
}
