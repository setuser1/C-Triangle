int main() {
    allocate int big(100) = 2147483648;
    free(big);
    return 0;
}
