class Metalscribe < Formula
  desc "100% local audio transcription and speaker diarization with Metal GPU acceleration"
  homepage "https://github.com/feliperbroering/metalscribe"
  url "https://github.com/feliperbroering/metalscribe/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "HOMEBREW_SHA256_PLACEHOLDER"
  license "MIT"
  
  head do
    url "https://github.com/feliperbroering/metalscribe.git", branch: "main"
  end

  depends_on "python@3.11"
  depends_on "ffmpeg"
  
  # Note on whisper.cpp:
  # whisper.cpp is a heavy C++ dependency that must be compiled with Metal support.
  # Rather than slow down every Homebrew install, metalscribe's doctor command
  # handles whisper.cpp setup intelligently:
  #   - Checks if already installed
  #   - Uses Homebrew cache for compilation
  #   - Only compiles once, not every time
  #
  # Alternative: pre-build whisper.cpp and host binary, but adds maintenance burden.

  def install
    # Create isolated virtual environment
    venv = libexec / "venv"
    system Formula["python@3.11"].opt_bin / "python3.11", "-m", "venv", venv
    
    # Upgrade pip, setuptools, wheel
    system venv / "bin/pip", "install", "--upgrade", "pip", "setuptools", "wheel"
    
    # Install metalscribe and dependencies in venv
    system venv / "bin/pip", "install", "-e", "."
    
    # Create executable wrapper in bin
    bin.write_exec_script venv / "bin" / "metalscribe"
  end

  def post_install
    # Verify CLI is accessible
    system "#{bin}/metalscribe", "--version"
    
    puts "\n" + "="*75
    puts "✓ metalscribe installed successfully!"
    puts "="*75
    puts "\nConfiguring dependencies (whisper.cpp, models, etc.)..."
    puts "This will take 15-40 minutes on first run (internet connection required)"
    puts ""
    
    # Run doctor --setup to:
    # 1. Compile whisper.cpp with Metal GPU support
    # 2. Download Whisper models
    # 3. Setup HuggingFace token for diarization
    # 4. Cache pyannote models
    system "#{bin}/metalscribe", "doctor", "--setup"
    
    puts "\n" + "="*75
    puts "✓ Setup complete! metalscribe is ready to use."
    puts "="*75
    puts "\nQuick start examples:"
    puts ""
    puts "  # Transcribe audio file"
    puts "  metalscribe transcribe --input audio.m4a --model medium --lang en"
    puts ""
    puts "  # Full pipeline (transcription + speaker diarization)"
    puts "  metalscribe run --input audio.m4a --model medium --speakers 2"
    puts ""
    puts "  # Verify dependencies"
    puts "  metalscribe doctor --check-only"
    puts ""
    puts "  # Get help"
    puts "  metalscribe --help"
    puts ""
    puts "Documentation: https://github.com/feliperbroering/metalscribe"
    puts "="*75 + "\n"
  end

  test do
    # Test version output
    assert_match(/0\.1\.0/, shell_output("#{bin}/metalscribe --version"))
    
    # Test help text
    assert_match(/usage:/, shell_output("#{bin}/metalscribe --help"))
    
    # Test doctor (dependency check)
    output = shell_output("#{bin}/metalscribe doctor --check-only")
    assert output.include?("python"), "Python should be detected"
    assert output.include?("ffmpeg"), "ffmpeg should be detected"
  end
end
