-- Bảng Users (Quản lý thông tin đăng nhập chung)
CREATE TABLE IF NOT EXISTS Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Doctor', 'Patient') NOT NULL
);

-- Bảng Admins (Thông tin chi tiết của Admin)
CREATE TABLE IF NOT EXISTS Admins (
    admin_id INT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,

    FOREIGN KEY (admin_id) REFERENCES Users(user_id)
);

-- Bảng Patients (Thông tin chi tiết của bệnh nhân, thêm avatar_url)
CREATE TABLE IF NOT EXISTS Patients (
    patient_id INT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    address TEXT,
    avatar_url VARCHAR(255), -- Đường dẫn ảnh đại diện

    FOREIGN KEY (patient_id) REFERENCES Users(user_id)
);


-- Bảng Departments (Thông tin khoa/phòng ban)
CREATE TABLE IF NOT EXISTS Departments (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

-- Bảng Doctors (Thông tin chi tiết của bác sĩ, thêm avatar_url)
CREATE TABLE IF NOT EXISTS Doctors (
    doctor_id INT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    address TEXT,
    description TEXT,
    avatar_url VARCHAR(255), -- Đường dẫn ảnh đại diện
    department_id INT NOT NULL,

    FOREIGN KEY (doctor_id) REFERENCES Users(user_id),
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
);



-- Bảng Appointments (Lịch khám)
CREATE TABLE IF NOT EXISTS Appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    department_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    shift ENUM('Shift 1', 'Shift 2', 'Shift 3', 'Shift 4') NOT NULL,
    description TEXT,
    status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id),
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
);

-- Bảng PatientHealthMetrics (Chỉ số sức khỏe bệnh nhân)
CREATE TABLE IF NOT EXISTS PatientHealthMetrics (
    metric_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    heart_rate INT,
    blood_pressure_systolic INT,
    blood_pressure_diastolic INT,
    blood_sugar_level FLOAT,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);

-- Bảng MedicalHistory (Lịch sử khám bệnh)
CREATE TABLE IF NOT EXISTS MedicalHistory (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    appointment_id INT NOT NULL,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    department_id INT NOT NULL,
    visit_date DATETIME NOT NULL,
    diagnosis TEXT,
    treatment TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id),
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id),
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
);

-- Bảng Notifications (Thông báo nhắc nhở)
CREATE TABLE IF NOT EXISTS Notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type ENUM('Appointment', 'Medication') NOT NULL,
    message TEXT NOT NULL,
    scheduled_time DATETIME NOT NULL,
    status ENUM('Pending', 'Sent', 'Failed') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);