-- Create users table (main table)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,

    INDEX idx_email (email)
);

-- Create departments table
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255),

    INDEX idx_name (name)
);

-- Create patients table with user_id as primary key
CREATE TABLE IF NOT EXISTS patients (
    id INT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    birthdate DATE,
    gender VARCHAR(10),
    address VARCHAR(255),

    INDEX idx_full_name (full_name),
    INDEX idx_email (email),
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create doctors table with user_id as primary key
CREATE TABLE IF NOT EXISTS doctors (
    id INT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    birthdate DATE,
    department_id INT,

    INDEX idx_email (email),
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

-- Create admins table with user_id as primary key
CREATE TABLE IF NOT EXISTS admins (
    id INT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,

    INDEX idx_email (email),
    INDEX idx_name (full_name),

    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);