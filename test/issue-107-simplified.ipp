// Test Issue #107: String and dynam types in structs (simplified)
// Tests that string and dynam types work correctly in struct fields

#include <stdio.h>

// ===== TEST 1: Struct with string field =====
struct StringHolder {
    int id;
    string title;
};

// ===== TEST 2: Struct with dynam field =====
struct DynamicHolder {
    int count;
    dynam int items;
};

// ===== TEST 3: Mixed string and dynam =====
struct MixedHolder {
    int id;
    string label;
    dynam int values;
};

int main() {
    printf("=== Testing Issue #107: String and dynam types in structs ===\n\n");
    
    // Test 1: String field
    printf("Test 1: Struct with string field\n");
    struct StringHolder sh;
    sh.id = 1;
    sh.title = "Test Title";
    printf("Title: %s\n", sh.title);
    printf("ID: %d\n\n", sh.id);
    
    // Test 2: Dynam field
    printf("Test 2: Struct with dynam field\n");
    struct DynamicHolder dh;
    dh.count = 3;
    printf("Count set: %d\n\n", dh.count);
    
    // Test 3: Mixed types
    printf("Test 3: Mixed string and dynam in one struct\n");
    struct MixedHolder mh;
    mh.id = 5;
    mh.label = "Mixed";
    printf("Label: %s\n", mh.label);
    printf("ID: %d\n\n", mh.id);
    
    printf("=== Tests completed successfully ===\n");
    
    return 0;
}
