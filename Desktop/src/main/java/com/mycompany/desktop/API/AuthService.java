package com.mycompany.desktop.API;

import com.mycompany.desktop.models.*;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Field;
import retrofit2.http.FormUrlEncoded;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.POST;
import retrofit2.http.Query;

public interface AuthService {

    @FormUrlEncoded
    @POST("login")
    Call<TokenResponse> login(
            @Field("username") String email,
            @Field("password") String password,
            @Field("role") String role);

    @POST("register/doctor")
    Call<Doctor> registerDoctor(
            @Header("Authorization") String token,
            @Body Doctor doctor);

    @GET("me/doctor")
    Call<Doctor> getDoctorProfile(@Header("Authorization") String token);

    @GET("me/admin")
    Call<Admin> getAdminProfile(@Header("Authorization") String token);

    @GET("departments")
    Call<List<Department>> getDepartments(@Header("Authorization") String token);

    @GET("doctors")
    Call<List<Doctor>> getListDoctors(
            @Header("Authorization") String token,
            @Query("department_id") Integer departmentId
    );

}
