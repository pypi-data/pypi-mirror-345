puts "Setup submodules"

# Change to the directory where this script is located
Dir.chdir(File.dirname(__FILE__))

# Clone submodules
if not File.directory?('cmake_utils')
  system('git clone --branch 1.0.0 --depth 1 https://github.com/SebastianoTaddei/cmake_utils.git cmake_utils')
else
  puts "cmake_utils already cloned. If you want to update it, delete the folder and run this script again."
end

if not File.directory?('submodules/GenericContainer')
  system('git clone --branch 1.1.4 --depth 1 https://github.com/SebastianoTaddei/GenericContainer.git submodules/GenericContainer')
  system('ruby submodules/GenericContainer/setup.rb')
else
  puts "GenericContainer already cloned. If you want to update it, delete the folder and run this script again."
end

if not File.directory?('submodules/UtilsLite')
  system('git clone --branch 1.0.4 --depth 1 https://github.com/SebastianoTaddei/UtilsLite.git submodules/UtilsLite')
  system('ruby submodules/UtilsLite/setup.rb')
else
  puts "UtilsLite already cloned. If you want to update it, delete the folder and run this script again."
end

if not File.directory?('submodules/quarticRootsFlocke')
  system('git clone --branch 1.1.4 --depth 1 https://github.com/SebastianoTaddei/quarticRootsFlocke.git submodules/quarticRootsFlocke')
  system('ruby submodules/quarticRootsFlocke/setup.rb')
else
  puts "quarticRootsFlocke already cloned. If you want to update it, delete the folder and run this script again."
end
