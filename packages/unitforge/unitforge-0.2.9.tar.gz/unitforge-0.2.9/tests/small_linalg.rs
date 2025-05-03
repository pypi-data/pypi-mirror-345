#[cfg(test)]
mod tests {
    use ndarray::arr1;
    use unitforge::quantities::*;
    use unitforge::small_linalg::{Matrix3, Vector3};
    use unitforge::PhysicsQuantity;

    pub fn approx_eq(a: f64, b: f64, epsilon: f64) -> bool {
        (a - b).abs() < epsilon
    }

    #[test]
    fn test_new() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        assert_eq!(matrix[(0, 0)], 1.0);
        assert_eq!(matrix[(2, 2)], 9.0);
    }

    #[test]
    fn test_zero() {
        let matrix: Matrix3<f64> = Matrix3::zero();
        assert_eq!(matrix[(0, 0)], 0_f64);
        assert_eq!(matrix[(0, 1)], 0_f64);
        assert_eq!(matrix[(0, 2)], 0_f64);
        assert_eq!(matrix[(0, 0)], 0_f64);
        assert_eq!(matrix[(1, 1)], 0_f64);
        assert_eq!(matrix[(2, 2)], 0_f64);
        assert_eq!(matrix[(0, 0)], 0_f64);
        assert_eq!(matrix[(1, 1)], 0_f64);
        assert_eq!(matrix[(2, 2)], 0_f64);
    }

    #[test]
    fn test_index() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        assert_eq!(matrix[(0, 0)], 1.0);
        assert_eq!(matrix[(1, 1)], 5.0);
        assert_eq!(matrix[(2, 2)], 9.0);
    }

    #[test]
    fn test_index_mut() {
        let mut matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        matrix[(0, 0)] = 10.0;
        matrix[(2, 2)] = 100.0;
        assert_eq!(matrix[(0, 0)], 10.0);
        assert_eq!(matrix[(2, 2)], 100.0);
    }

    #[test]
    fn test_det() {
        let matrix1 = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        assert_eq!(matrix1.det(), 0.0); // This matrix is singular, so determinant should be 0

        let matrix2 = Matrix3::new([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]);
        assert_eq!(matrix2.det(), 1.0); // Identity matrix, determinant should be 1

        let matrix3: Matrix3<Distance> =
            Matrix3::from_f64([[6.0, 1.0, 1.0], [4.0, -2.0, 5.0], [2.0, 8.0, 7.0]]);
        let deviation = (matrix3.det() - Volume::new(-306.0, VolumeUnit::mcb)).abs();
        assert!(deviation.to_raw() < f64::EPSILON);
    }

    #[test]
    fn test_inverse() {
        let matrix1 = Matrix3::new([[1.0, 2.0, 3.0], [0.0, 1.0, 4.0], [5.0, 6.0, 0.0]]);
        let expected_inv1 =
            Matrix3::new([[-24.0, 18.0, 5.0], [20.0, -15.0, -4.0], [-5.0, 4.0, 1.0]]);
        assert_eq!(matrix1.inverse(), Some(expected_inv1));

        let matrix2 = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        assert_eq!(matrix2.inverse(), None); // This matrix is singular, so no inverse exists
    }

    #[test]
    fn test_inverse_distance() {
        let d = Distance::new(2., DistanceUnit::mm);
        let a = d * d;
        let v = d * d * d;
        let inverse_distance = a / v;
        assert!(approx_eq(
            inverse_distance.to(InverseDistanceUnit::_m),
            500.,
            10E-10
        ));

        let matrix1: Matrix3<Distance> =
            Matrix3::from_f64([[1.0, 2.0, 3.0], [0.0, 1.0, 4.0], [5.0, 6.0, 0.0]]);
        let expected_inv1: Matrix3<InverseDistance> =
            Matrix3::from_f64([[-24.0, 18.0, 5.0], [20.0, -15.0, -4.0], [-5.0, 4.0, 1.0]]);
        let inv = matrix1.inverse().unwrap();
        let diff = (expected_inv1 - inv).frobenius_norm();
        assert!(diff.to_raw() < f64::EPSILON);
    }

    #[test]
    fn test_dot() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        let vector = Vector3::new([1.0, 0.0, -1.0]);
        let result = matrix.dot(&vector);
        assert_eq!(result, Vector3::new([-2.0, -2.0, -2.0]));
    }

    #[test]
    fn test_add_assign_vector3() {
        let mut v1: Vector3<Distance> = Vector3::from_f64([1.0, 2.0, 3.0]);
        let v2 = Vector3::from_f64([4.0, 5.0, 6.0]);

        v1 += v2;
        assert_eq!(v1, Vector3::from_f64([5.0, 7.0, 9.0]));
    }

    #[test]
    fn test_sub_assign_vector3() {
        let mut v1 = Vector3::new([1.0, 2.0, 3.0]);
        let v2 = Vector3::new([4.0, 5.0, 6.0]);

        v1 -= v2;

        assert_eq!(v1.data(), [-3.0, -3.0, -3.0]);
    }

    #[test]
    fn test_add_vector3() {
        let v1 = Vector3::new([1.0, 2.0, 3.0]);
        let v2 = Vector3::new([4.0, 5.0, 6.0]);

        let v3 = v1 + v2;

        assert_eq!(v3.data(), [5.0, 7.0, 9.0]);
    }

    #[test]
    fn test_sub_vector3() {
        let v1 = Vector3::new([1.0, 2.0, 3.0]);
        let v2 = Vector3::new([4.0, 5.0, 6.0]);

        let v3 = v1 - v2;

        assert_eq!(v3.data(), [-3.0, -3.0, -3.0]);
    }

    #[test]
    fn test_vector3_from_ndarray() {
        let data = arr1(&[1., 2., 3.]);
        let v = Vector3::from_ndarray(data.view()).unwrap();
        for i in 0..3 {
            assert_eq!(v[i], data[i]);
        }
    }

    #[test]
    fn test_vector3_to_ndarray() {
        let v = Vector3::new([2.0, 1.0, 4.0]);
        let nd = v.to_ndarray();
        for i in 0..3 {
            assert!(approx_eq(nd[i], v[i], 1e-10));
        }
    }

    #[test]
    fn test_cross_product_basic() {
        let v1: Vector3<Force> = Vector3::from_f64([1.0, 0.0, 0.0]);
        let v2: Vector3<Distance> = Vector3::from_f64([0.0, 1.0, 0.0]);
        let cross_product: Vector3<ForceDistance> = v1.cross(&v2);
        assert_eq!(cross_product, Vector3::from_f64([0.0, 0.0, 1.0]));
    }

    #[test]
    fn test_cross_product_with_negative_values() {
        let v1 = Vector3::new([-1.0, 2.0, 3.0]);
        let v2 = Vector3::new([4.0, 0.0, -8.0]);
        let cross_product = v1.cross(&v2);
        assert_eq!(cross_product.data(), [-16.0, 4.0, -8.0]);
    }

    #[test]
    fn test_cross_product_with_zero_vector() {
        let v1 = Vector3::new([0.0, 0.0, 0.0]);
        let v2 = Vector3::new([1.0, 2.0, 3.0]);
        let cross_product = v1.cross(&v2);
        assert_eq!(cross_product.data(), [0.0, 0.0, 0.0]);
    }

    #[test]
    fn test_cross_product_of_parallel_vectors() {
        let v1 = Vector3::new([1.0, 2.0, 3.0]);
        let v2 = Vector3::new([2.0, 4.0, 6.0]);
        let cross_product = v1.cross(&v2);
        assert_eq!(cross_product.data(), [0.0, 0.0, 0.0]);
    }

    #[test]
    fn test_cross_product_of_anti_parallel_vectors() {
        let v1 = Vector3::new([1.0, 2.0, 3.0]);
        let v2 = Vector3::new([-1.0, -2.0, -3.0]);
        let cross_product = v1.cross(&v2);
        assert_eq!(cross_product.data(), [0.0, 0.0, 0.0]);
    }

    #[test]
    fn test_norm_of_zero_vector() {
        let v = Vector3::new([0.0, 0.0, 0.0]);
        assert!((v.norm() - 0_f64).abs() < f64::EPSILON);
    }

    #[test]
    fn test_norm_of_unit_vectors() {
        let vx = Vector3::new([1.0, 0.0, 0.0]);
        let vy = Vector3::new([0.0, 1.0, 0.0]);
        let vz = Vector3::new([0.0, 0.0, 1.0]);

        assert!((vx.norm() - 1_f64).abs() < f64::EPSILON);
        assert!((vy.norm() - 1_f64).abs() < f64::EPSILON);
        assert!((vz.norm() - 1_f64).abs() < f64::EPSILON);
    }

    #[test]
    fn test_norm_of_arbitrary_vector() {
        let v = Vector3::new([3.0, 4.0, 0.0]);
        assert!((v.norm() - 5_f64).abs() < f64::EPSILON); // 3-4-5 right triangle
    }

    #[test]
    fn test_norm_of_negative_components() {
        let v = Vector3::new([-1.0, -2.0, -2.0]);
        assert!((v.norm() - 3_f64).abs() < f64::EPSILON); // sqrt(1 + 4 + 4) = 3
    }

    #[test]
    fn test_to_unit_vector() {
        let v = Vector3::new([
            Force::new(1.0, ForceUnit::N),
            Force::new(-2.0, ForceUnit::N),
            Force::new(-2.0, ForceUnit::N),
        ]);
        let u = v.to_unit_vector();
        assert!((u.norm() - 1.).abs().to_raw() < f64::EPSILON);
        let collinearity = v.to_raw().dot_vct(&u) / v.norm().to_raw();
        assert!((collinearity - 1_f64).abs() < f64::EPSILON);
    }

    #[test]
    fn test_quantity_times_vector() {
        let f = Force::new(1., ForceUnit::kN);
        let v = Vector3::new([0., 1., 0.]);
        let f_v = f * v;
        assert!((f_v[0] - Force::new(0., ForceUnit::kN)).to_raw().abs() < f64::EPSILON);
        assert!((f_v[1] - Force::new(1., ForceUnit::kN)).to_raw().abs() < f64::EPSILON);
        assert!((f_v[2] - Force::new(0., ForceUnit::kN)).to_raw().abs() < f64::EPSILON);
    }

    #[test]
    fn test_norm_of_non_integer_values() {
        let v = Vector3::new([0.5, 0.5, 0.5]);
        assert!((v.norm() - (0.75_f64).sqrt()).abs() < f64::EPSILON); // sqrt(0.25 + 0.25 + 0.25)
    }

    #[test]
    fn test_vector3_mul() {
        let v: Vector3<Force> = Vector3::from_f64([1.0, 2.0, 3.0]);
        let result = v * 2.0;
        assert_eq!(
            result,
            Vector3::new([
                Force::new(2.0, ForceUnit::N),
                Force::new(4.0, ForceUnit::N),
                Force::new(6.0, ForceUnit::N)
            ])
        );
    }

    #[test]
    fn test_vector3_f64_mul_with_quantity() {
        let v: Vector3<f64> = Vector3::from_f64([1.0, 2.0, 3.0]);
        let result = v * Distance::new(2.0, DistanceUnit::m);
        assert_eq!(
            result,
            Vector3::new([
                Distance::new(2.0, DistanceUnit::m),
                Distance::new(4.0, DistanceUnit::m),
                Distance::new(6.0, DistanceUnit::m)
            ])
        );
    }

    #[test]
    fn test_vector3_mul_quantities() {
        let v: Vector3<Force> = Vector3::from_f64([1.0, 2.0, 3.0]);
        let scalar = Distance::new(2., DistanceUnit::m);
        let result = v * scalar;
        assert_eq!(
            result,
            Vector3::new([
                ForceDistance::new(2.0, ForceDistanceUnit::Nm),
                ForceDistance::new(4.0, ForceDistanceUnit::Nm),
                ForceDistance::new(6.0, ForceDistanceUnit::Nm)
            ])
        );
    }

    #[test]
    fn test_vector3_mul_vector3() {
        let a = Vector3::new([1., 2., 3.]);
        let b = Vector3::new([2., 4., 6.]);
        let result = a * b;
        assert_eq!(result, Vector3::new([2., 8., 18.]));
    }

    #[test]
    fn test_vector3_mul_vector3_quantities() {
        let forces: Vector3<Force> = Vector3::from_f64([1.0, 2.0, 3.0]);
        let distances = Vector3::new([
            Distance::new(2.0, DistanceUnit::m),
            Distance::new(3.0, DistanceUnit::m),
            Distance::new(4.0, DistanceUnit::m),
        ]);
        let result = forces * distances;
        let expected = Vector3::new([
            ForceDistance::new(2.0, ForceDistanceUnit::Nm),
            ForceDistance::new(6.0, ForceDistanceUnit::Nm),
            ForceDistance::new(12.0, ForceDistanceUnit::Nm),
        ]);
        assert!((result - expected).norm().to_raw() < 10E-10);
    }
    #[test]
    fn test_vector3_div() {
        let v: Vector3<Distance> = Vector3::from_f64([2.0, 4.0, 6.0]);
        let result = v / 2.0;
        assert_eq!(
            result,
            Vector3::new([
                Distance::new(1.0, DistanceUnit::m),
                Distance::new(2.0, DistanceUnit::m),
                Distance::new(3.0, DistanceUnit::m)
            ])
        );
    }

    #[test]
    fn test_vector3_mul_assign() {
        let mut v = Vector3::new([1.0, 2.0, 3.0]);
        v *= 2.0;
        assert_eq!(v, Vector3::new([2.0, 4.0, 6.0]));
    }

    #[test]
    fn test_vector3_div_assign() {
        let mut v = Vector3::new([2.0, 4.0, 6.0]);
        v /= 2.0;
        assert_eq!(v, Vector3::new([1.0, 2.0, 3.0]));
    }

    #[test]
    fn test_dot_vct_vector3() {
        let v1: Vector3<Force> = Vector3::from_f64([2.0, 4.0, 6.0]);
        let v2: Vector3<Distance> = Vector3::from_f64([1.0, 2.0, 3.0]);
        assert!(approx_eq(
            v1.dot_vct(&v2).to(ForceDistanceUnit::Nm),
            28.,
            1e-10
        ));
        assert!(approx_eq(
            v1.dot_vct(&v2).to(ForceDistanceUnit::Nm),
            28.,
            1e-10
        ));
    }

    #[test]
    fn vector3_times_scalar() {
        let vector = Vector3::new([1.0, 2.0, 3.0]);
        let scalar = 2.0;
        let result = vector * scalar;
        assert_eq!(result.data(), [2.0, 4.0, 6.0]);
    }

    #[test]
    fn scalar_times_vector3() {
        let scalar = 3.0;
        let vector = Vector3::new([1.0, 2.0, 3.0]);
        let result = vector * scalar;
        assert_eq!(result.data(), [3.0, 6.0, 9.0]);
    }

    #[test]
    fn vector3_times_zero_scalar() {
        let vector = Vector3::new([1.0, 2.0, 3.0]);
        let scalar = 0.0;
        let result = vector * scalar;
        assert_eq!(result.data(), [0.0, 0.0, 0.0]);
    }

    #[test]
    fn vector3_zero_scalar_times_vector3() {
        let scalar = 0.0;
        let vector = Vector3::new([1.0, 2.0, 3.0]);
        let result = vector * scalar;
        assert_eq!(result.data(), [0.0, 0.0, 0.0]);
    }

    #[test]
    fn test_add_matrix3() {
        let mat1 = Matrix3::new([[1_f64; 3]; 3]);
        let mat2 = Matrix3::new([[2_f64; 3]; 3]);
        let result = mat1 + mat2;
        let expected = Matrix3::new([[3_f64; 3]; 3]);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_sub_matrix3() {
        let mat1 = Matrix3::new([[3_f64; 3]; 3]);
        let mat2 = Matrix3::new([[2_f64; 3]; 3]);
        let result = mat1 - mat2;
        let expected = Matrix3::new([[1_f64; 3]; 3]);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_add_assign_matrix3() {
        let mut mat1 = Matrix3::new([[1_f64; 3]; 3]);
        let mat2 = Matrix3::new([[2_f64; 3]; 3]);
        mat1 += mat2;
        let expected = Matrix3::new([[3_f64; 3]; 3]);
        assert_eq!(mat1, expected);
    }

    #[test]
    fn test_sub_assign_matrix3() {
        let mut mat1 = Matrix3::new([[3_f64; 3]; 3]);
        let mat2 = Matrix3::new([[2_f64; 3]; 3]);
        mat1 -= mat2;
        let expected = Matrix3::new([[1_f64; 3]; 3]);
        assert_eq!(mat1, expected);
    }

    #[test]
    fn test_vector_element_times_matrix3() {
        let mat = Matrix3::new([[3_f64; 3]; 3]);
        let f = Force::new(1., ForceUnit::kN);
        let res = f * mat;
        for i in 0..3 {
            for j in 0..3 {
                assert_eq!(res[(i, j)], Force::new(3., ForceUnit::kN))
            }
        }
    }

    #[test]
    fn test_matrix3_times_vector_element() {
        let mat = Matrix3::new([[3_f64; 3]; 3]);
        let f = Force::new(1., ForceUnit::kN);
        let res = mat * f;
        for i in 0..3 {
            for j in 0..3 {
                assert_eq!(res[(i, j)], Force::new(3., ForceUnit::kN))
            }
        }
    }

    #[test]
    fn test_matrix3_dot() {
        let mat: Matrix3<Distance> = Matrix3::from_f64([[4., 7., 2.], [0., 3., 9.], [5., 1., 3.]]);
        let v: Vector3<Distance> = Vector3::from_f64([2., 6., 5.]);
        let res = mat.dot(&v);
        let expected: Vector3<Area> = Vector3::from_f64([60., 63., 31.]);
        assert!((res - expected).norm().to_raw() < f64::EPSILON);
    }

    #[test]
    fn test_solve() {
        let matrix = Matrix3::new([[2.0, -1.0, 0.0], [-1.0, 2.0, -1.0], [0.0, -1.0, 2.0]]);
        let rhs = Vector3::new([1.0, 0.0, 1.0]);
        let solution = matrix.solve(&rhs);

        assert!(solution.is_some());
        let sol = solution.unwrap();

        assert!((matrix.dot(&sol) - rhs)
            .data
            .iter()
            .all(|&x| x.abs() < 1e-6));
    }

    #[test]
    fn test_qr_decomposition() {
        let a = Matrix3::new([[12.0, -51.0, 4.0], [6.0, 167.0, -68.0], [-4.0, 24.0, -41.0]]);

        let (q, r) = a.qr_decomposition();

        let identity = q.transpose() * q;
        let expected_identity = Matrix3::identity();
        for i in 0..3 {
            for j in 0..3 {
                assert!((identity[(i, j)] - expected_identity[(i, j)]).abs() < 1e-6);
            }
        }
        let recomposed = q * r;
        for i in 0..3 {
            for j in 0..3 {
                assert!((recomposed[(i, j)] - a[(i, j)]).abs() < 1e-6);
            }
        }
    }

    #[test]
    fn test_qr_eigenvalues() {
        let a = Matrix3::new([[4.0, -2.0, 1.0], [-2.0, 4.0, -2.0], [1.0, -2.0, 3.0]]);

        let eigen_pairs = a.qr_eigen(100, 1e-9);

        let expected_eigenvalues = [1.31260044, 2.56837289, 7.11902668];
        for (i, ev) in eigen_pairs.iter().enumerate() {
            assert!((ev.0 - expected_eigenvalues[i]).abs() < 1e-6);
        }
    }

    #[test]
    fn test_qr_eigenvectors() {
        let a = Matrix3::new([[4.0, -2.0, 1.0], [-2.0, 4.0, -2.0], [1.0, -2.0, 3.0]]);

        let eigen_pairs = a.qr_eigen(100, 1e-9);
        for i in 0..3 {
            let lambda = eigen_pairs[i].0;
            let v = eigen_pairs[i].1;
            let av = a.dot(&v);
            let expected = v * lambda;
            assert!((av - expected).norm() < 1e-6);
        }
    }

    #[test]
    fn test_get_column() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);

        assert_eq!(matrix.get_column(0).data, [1.0, 4.0, 7.0]);
        assert_eq!(matrix.get_column(1).data, [2.0, 5.0, 8.0]);
        assert_eq!(matrix.get_column(2).data, [3.0, 6.0, 9.0]);
    }

    #[test]
    fn test_set_column() {
        let mut matrix = Matrix3::zero();
        let column = Vector3::new([1.0, 2.0, 3.0]);
        matrix.set_column(1, column);

        assert_eq!(matrix[(0, 1)], 1.0);
        assert_eq!(matrix[(1, 1)], 2.0);
        assert_eq!(matrix[(2, 1)], 3.0);
    }

    #[test]
    fn test_get_row() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);

        assert_eq!(matrix.get_row(0), Vector3::new([1.0, 2.0, 3.0]));
        assert_eq!(matrix.get_row(1), Vector3::new([4.0, 5.0, 6.0]));
        assert_eq!(matrix.get_row(2), Vector3::new([7.0, 8.0, 9.0]));
    }

    #[test]
    fn test_set_row() {
        let mut matrix = Matrix3::zero();
        let row = Vector3::new([1.0, 2.0, 3.0]);
        matrix.set_row(1, row);

        assert_eq!(matrix[(1, 0)], 1.0);
        assert_eq!(matrix[(1, 1)], 2.0);
        assert_eq!(matrix[(1, 2)], 3.0);
    }

    #[test]
    fn test_from_rows() {
        let rows = [
            Vector3::new([1.0, 2.0, 3.0]),
            Vector3::new([4.0, 5.0, 6.0]),
            Vector3::new([7.0, 8.0, 9.0]),
        ];
        let matrix = Matrix3::from_rows(&rows);
        for i in 0..3 {
            assert!((matrix.get_row(i) - rows[i]).norm() < 1E-10);
        }
    }

    #[test]
    fn test_from_columns() {
        let columns = [
            Vector3::new([1.0, 4.0, 7.0]),
            Vector3::new([2.0, 5.0, 8.0]),
            Vector3::new([3.0, 6.0, 9.0]),
        ];
        let matrix = Matrix3::from_columns(&columns);
        for i in 0..3 {
            assert!((matrix.get_column(i) - columns[i]).norm() < 1E-10);
        }
    }

    #[test]
    fn test_transpose() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        let transposed = matrix.transpose();
        for i in 0..3 {
            for j in 0..3 {
                assert_eq!(matrix[(i, j)], transposed[(j, i)]);
            }
        }
    }

    #[test]
    fn test_matrix_multiplication() {
        let a = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        let b = Matrix3::new([[9.0, 8.0, 7.0], [6.0, 5.0, 4.0], [3.0, 2.0, 1.0]]);
        let result = a * b;
        let expected = Matrix3::new([[30.0, 24.0, 18.0], [84.0, 69.0, 54.0], [138.0, 114.0, 90.0]]);
        for i in 0..3 {
            for j in 0..3 {
                assert_eq!(result[(i, j)], expected[(i, j)]);
            }
        }
    }
}
