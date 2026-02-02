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
  # Note: whisper.cpp is compiled from source during installation
  # or users can install via: brew tap ggerganov/whisper.cpp && brew install whisper.cpp

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
    # Verify installation completed
    system "#{bin}/metalscribe", "--version"
    
    # Inform user about next steps
    puts "\n" + "="*60
    puts "✓ metalscribe installed successfully!"
    puts "="*60
    puts "\nNext step: Setup dependencies (whisper.cpp models, pyannote cache)"
    puts "\n  metalscribe doctor --setup"
    puts "\nFor more info:"
    puts "  metalscribe --help"
    puts "="*60 + "\n"
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
