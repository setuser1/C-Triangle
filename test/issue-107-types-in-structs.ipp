// Test Issue #107: Base types inside structs don't work
// Testing C11-style struct syntax to see if types work

#include <stdio.h>

// ===== TEST 1: C11 Plain struct with string field =====
struct StringHolder {
    int id;
    string title;
};

// ===== TEST 2: C11 Plain struct with dynam field =====
struct DynamicHolder {
    int count;
    dynam int items;
};

// ===== TEST 3: C11 Plain struct with tuple field =====
struct TupleHolder {
    int id;
    tuple data;
};

// ===== TEST 5: Mixed types without auto =====
struct MixedHolder {
    int id;
    string label;
    int count;
    dynam int values;
    tuple metadata;
};

int main() {
    printf("=== Testing Issue #107: Base types in C11 structs ===\n\n");
    
    // Test 1: String field
    printf("Test 1: Struct with string field\n");
    struct StringHolder sh;
    sh.id = 1;
    sh.title = "Test Title";
    printf("Title: %k\n\n", sh.title);
    
    // Test 2: Dynam field
    printf("Test 2: Struct with dynam field\n");
    struct DynamicHolder dh;
    dh.count = 3;
    dh.items = [1, 2, 3];
    printf("Item count: %d\n\n", len(dh.items));
    
    // Test 3: Tuple field
    printf("Test 3: Struct with tuple field\n");
    struct TupleHolder th;
    th.id = 1;
    th.data = [42, "test", 3.14];
    printf("First element: %k\n\n", th.data[0]);
    
    // Test 5: Mixed types
    printf("Test 4: Mixed types in one struct\n");
    struct MixedHolder mh;
    mh.id = 5;
    mh.label = "Mixed";
    mh.count = 2;
    mh.values = [5, 10, 15];
    mh.metadata = [999, "mixed", 1.5];
    printf("Label: %k, Count: %d\n\n", mh.label, mh.count);
    
    printf("=== All tests completed ===\n");
    
    return 0;
}
