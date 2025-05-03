class HP:
    codes = [
        '''
#include <iostream>
#include <omp.h>

int main() {
    int n;
    std::cout << "Enter a number: ";
    std::cin >> n;

    if (n < 0) {
        std::cout << "Factorial not defined for negative numbers." << std::endl;
        return 1;
    }

    unsigned long long factorial = 1;
    double start_time = omp_get_wtime();

    #pragma omp parallel for reduction(*:factorial)
    for (int i = 1; i <= n; i++) {
        factorial *= i;
    }

    double end_time = omp_get_wtime();
    std::cout << "Parallel Factorial of " << n << " is: " << factorial << std::endl;
    std::cout << "Parallel Execution Time: " << (end_time - start_time) << " seconds\n";

    return 0;
}

int main() {
    int n;
    std::cout << "Enter a number: ";
    std::cin >> n;

    if (n < 0) {
        std::cout << "Factorial not defined for negative numbers." << std::endl;
        return 1;
    }

    unsigned long long factorial = 1;
    double start_time = omp_get_wtime();

    for (int i = 1; i <= n; i++) {
        factorial *= i;
    }

    double end_time = omp_get_wtime();
    std::cout << "Serial Factorial of " << n << " is: " << factorial << std::endl;
    std::cout << "Serial Execution Time: " << (end_time - start_time) << " seconds\n";

    return 0;
}
        ''',
        '''
#include <iostream>
#include <omp.h>

double f(double x) { return x * x; }

int main() {
    double a, b, integral = 0.0, h;
    int n, num_threads;

    std::cout << "Enter a, b, n, and number of threads: ";
    std::cin >> a >> b >> n >> num_threads;

    if (n % num_threads != 0) {
        std::cerr << "Error: n must be divisible by number of threads.\n";
        return 1;
    }

    h = (b - a) / n;
    double start_time = omp_get_wtime();

    integral += (f(a) + f(b)) / 2.0;

#pragma omp parallel for num_threads(num_threads) reduction(+:integral)
    for (int i = 1; i < n; ++i)
        integral += f(a + i * h);

    integral *= h;

    std::cout << "Approximated Integral = " << integral << "\n";
    std::cout << "Computation Time: " << omp_get_wtime() - start_time << " seconds\n";

    return 0;
}
        ''',
        '''
#include <mpi.h>
#include <iostream>
#include <vector>
#include <numeric>

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    const int ARRAY_SIZE = 10;
    std::vector<int> data(ARRAY_SIZE);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (size < 3) {
        if (rank == 0) std::cerr << "Run with at least 3 processes.\n";
        MPI_Finalize();
        return 1;
    }

    int local_sum = 0;
    double start_time = 0.0;

    if (rank == 0 || rank == 1) {
        for (int i = rank * ARRAY_SIZE / 2; i < (rank + 1) * ARRAY_SIZE / 2; ++i)
            data[i] = i + 1;

        MPI_Send(&data[rank * ARRAY_SIZE / 2], ARRAY_SIZE / 2, MPI_INT, 2, 0, MPI_COMM_WORLD);
        local_sum = std::accumulate(data.begin() + rank * ARRAY_SIZE / 2, data.begin() + (rank + 1) * ARRAY_SIZE / 2, 0);
        MPI_Send(&local_sum, 1, MPI_INT, 2, 1, MPI_COMM_WORLD);
    }

    else if (rank == 2) {
        start_time = MPI_Wtime();

        std::vector<int> recv_data(ARRAY_SIZE);
        int sum1, sum2;

        MPI_Recv(&recv_data[0], ARRAY_SIZE / 2, MPI_INT, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Recv(&recv_data[ARRAY_SIZE / 2], ARRAY_SIZE / 2, MPI_INT, 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Recv(&sum1, 1, MPI_INT, 0, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Recv(&sum2, 1, MPI_INT, 1, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

        std::cout << "Final Sum = " << sum1 + sum2 << "\n";
        std::cout << "Total Time Taken = " << MPI_Wtime() - start_time << " seconds\n";
    }

    MPI_Finalize();
    return 0;
}

To Run
mpiexec -n 4 MPI.exec
        ''',
        '''
#include <mpi.h>
#include <iostream>
#include <vector>

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int rank, size, n = 10;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (size < 4) { if (rank == 0) std::cerr << "Need 4+ processes\n"; MPI_Finalize(); return 1; }

    std::vector<double> data(n);
    if (rank == 0) {
        for (int i = 0; i < n; ++i) data[i] = i + 1.0 - 4;
        MPI_Send(data.data(), n, MPI_DOUBLE, 1, 0, MPI_COMM_WORLD);
    }
    else {
        MPI_Recv(data.data(), n, MPI_DOUBLE, rank - 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        for (double& x : data)
            if (rank == 1) x /= 5.0;
            else if (rank == 2) x += 3.0;
            else if (rank == 3) x *= 7.0;
        if (rank < 3) MPI_Send(data.data(), n, MPI_DOUBLE, rank + 1, 0, MPI_COMM_WORLD);
        else { for (double x : data) std::cout << x << " "; std::cout << "\n"; }
    }

    MPI_Finalize();
    return 0;
}

To run 
mpiexec -n 4 Pipeline.exe
        ''',
        '''
#include <mpi.h>
#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdlib>
#include <ctime>

void bubble_sort(std::vector<int>& arr) {
    for (int i = 0; i < arr.size() - 1; ++i)
        for (int j = 0; j < arr.size() - i - 1; ++j)
            if (arr[j] > arr[j + 1]) std::swap(arr[j], arr[j + 1]);
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    const int total_elements = 16;
    int local_size = total_elements / size;
    std::vector<int> full_array, local_array(local_size);

    if (rank == 0) {
        full_array.resize(total_elements);
        std::srand(static_cast<unsigned int>(std::time(nullptr)));
        for (auto& x : full_array) x = std::rand() % 100;
        std::cout << "Unsorted Array: ";
        for (int x : full_array) std::cout << x << " ";
        std::cout << "\n";
    }

    MPI_Scatter(full_array.data(), local_size, MPI_INT, local_array.data(), local_size, MPI_INT, 0, MPI_COMM_WORLD);
    bubble_sort(local_array);

    for (int phase = 0; phase < size; ++phase) {
        int partner = (phase % 2 == 0) ? ((rank % 2 == 0 && rank + 1 < size) ? rank + 1 : rank - 1)
                                      : ((rank % 2 != 0 && rank + 1 < size) ? rank + 1 : rank - 1);

        if (partner >= 0 && partner < size) {
            std::vector<int> recv_array(local_size);
            MPI_Sendrecv(local_array.data(), local_size, MPI_INT, partner, 0, recv_array.data(), local_size, MPI_INT, partner, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

            std::vector<int> merged(2 * local_size);
            std::merge(local_array.begin(), local_array.end(), recv_array.begin(), recv_array.end(), merged.begin());
            std::copy(merged.begin() + (rank < partner ? 0 : local_size), merged.begin() + (rank < partner ? local_size : 2 * local_size), local_array.begin());
        }
    }

    MPI_Gather(local_array.data(), local_size, MPI_INT, full_array.data(), local_size, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        std::cout << "Sorted Array: ";
        for (int x : full_array) std::cout << x << " ";
        std::cout << "\n";
    }

    MPI_Finalize();
    return 0;
}
        ''',
        '''
%%writefile perfect_number.cu
#include <stdio.h>

__global__ void perfect() {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int num = tid + 1;

    if (num > 10000 || num < 2) return;

    int sum = 1;
    for (int i = 2; i <= num / 2; ++i) {
        if (num % i == 0) sum += i;
    }

    if (sum == num) {
        printf("%d is a perfect number\n", num);
    }
}

int main() {
    int totalNumbers = 10000;
    int threadsPerBlock = 256;
    int numBlocks = (totalNumbers + threadsPerBlock - 1) / threadsPerBlock;

    perfect<<<numBlocks, threadsPerBlock>>>();
    cudaDeviceSynchronize();

    return 0;
}


To Run
!nvcc -arch=sm_75 -o perfect_number perfect_number.cu

./perfect_number
        ''',
        '''
%%writefile matrix_mul.cu
#include <iostream>
#include <cuda_runtime.h>
#define N 4
#define BLOCK_SIZE 4

__global__ void matMulKernel(float* A, float* B, float* C, int n) {
    int row = blockIdx.y * BLOCK_SIZE + threadIdx.y;
    int col = blockIdx.x * BLOCK_SIZE + threadIdx.x;
    float sum = 0.0f;
    for (int k = 0; k < n; ++k)
        if (row < n && col < n) sum += A[row * n + k] * B[k * n + col];
    if (row < n && col < n) C[row * n + col] = sum;
}

void printMatrix(float* mat, int n, const char* name) {
    std::cout << name << ":\n";
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) std::cout << mat[i * n + j] << " ";
        std::cout << "\n";
    }
}

int main() {
    size_t size = N * N * sizeof(float);
    float *h_A = new float[N * N], *h_B = new float[N * N], *h_C = new float[N * N];
    for (int i = 0; i < N * N; ++i) h_A[i] = h_B[i] = rand() % 101;

    float *d_A, *d_B, *d_C;
    cudaMalloc(&d_A, size); cudaMalloc(&d_B, size); cudaMalloc(&d_C, size);
    cudaMemcpy(d_A, h_A, size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B, size, cudaMemcpyHostToDevice);

    dim3 threads(BLOCK_SIZE, BLOCK_SIZE);
    dim3 blocks((N + BLOCK_SIZE - 1) / BLOCK_SIZE, (N + BLOCK_SIZE - 1) / BLOCK_SIZE);
    matMulKernel<<<blocks, threads>>>(d_A, d_B, d_C, N);

    cudaMemcpy(h_C, d_C, size, cudaMemcpyDeviceToHost);

    if (N <= 16) {
        printMatrix(h_A, N, "Matrix A");
        printMatrix(h_B, N, "Matrix B");
        printMatrix(h_C, N, "Matrix C");
    }

    cudaFree(d_A); cudaFree(d_B); cudaFree(d_C);
    delete[] h_A; delete[] h_B; delete[] h_C;
    return 0;
}

!nvcc matrix_mul.cu -o matrix_mul -arch=sm_75

!./matrix_mul
        ''',
    ]

    @staticmethod
    def text(index):
        """Fetch a specific code based on the index."""
        try:
            return HP.codes[index - 1]
        except IndexError:
            return f"Invalid code index. Please choose a number between 1 and {len(HP.codes)}."
