#include <curl/curl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to create a session by making a POST request to the server
void create_session_c(const char* base_url, int source_model_ID, int destination_model_ID, 
                      const char* client_id, int initiator_id, int inviter_id,
                      int* input_variables_ID, int* input_variables_size, 
                      int no_of_input_variables, int* output_variables_ID, int* output_variables_size, 
                      int no_of_output_variables) {
    CURL *curl;
    CURLcode res;

    // Buffers for constructing URLs and POST fields
    char full_url[1024]; // Buffer to construct the full URL
    char postFields[2048]; // Buffer for JSON payload

    // Construct the URL with the client_id appended to create a session
    snprintf(full_url, sizeof(full_url), "%s/create_session/%s", base_url, client_id);

    // Start constructing the JSON payload with model IDs, client ID, initiator ID, and inviter ID
    sprintf(postFields, "{\"source_model_ID\": \"%d\", \"destination_model_ID\": \"%d\", \"client_id\": \"%s\", \"initiator_id\": \"%d\", \"inviter_id\": \"%d\", ", 
            source_model_ID, destination_model_ID, client_id, initiator_id, inviter_id);

    // Buffer for temporary storage of array strings
    char arrays[1024]; // Ensure this buffer is large enough for your needs

    // Constructing JSON array of input_variables_ID
    strcat(postFields, "\"input_variables_ID\": [");
    for (int i = 0; i < no_of_input_variables; ++i) {
        // Append comma between elements, but not before the first element
        if(i > 0) strcat(postFields, ", ");
        sprintf(arrays, "%d", input_variables_ID[i]);
        strcat(postFields, arrays);
    }

    // Constructing JSON array of input_variables_size
    strcat(postFields, "], \"input_variables_size\": [");
    for (int i = 0; i < no_of_input_variables; ++i) {
        if(i > 0) strcat(postFields, ", ");
        sprintf(arrays, "%d", input_variables_size[i]);
        strcat(postFields, arrays);
    }

    // Repeat the process for output_variables_ID and output_variables_size
    strcat(postFields, "], \"output_variables_ID\": [");
    for (int i = 0; i < no_of_output_variables; ++i) {
        if(i > 0) strcat(postFields, ", ");
        sprintf(arrays, "%d", output_variables_ID[i]);
        strcat(postFields, arrays);
    }
    strcat(postFields, "], \"output_variables_size\": [");
    for (int i = 0; i < no_of_output_variables; ++i) {
        if(i > 0) strcat(postFields, ", ");
        sprintf(arrays, "%d", output_variables_size[i]);
        strcat(postFields, arrays);
    }

    // Close the JSON payload
    strcat(postFields, "]}");

    // Initialize CURL session
    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();

    if(curl) {
        // Set headers for JSON content type
        struct curl_slist *headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");

        // Set CURL options for the POST request
        curl_easy_setopt(curl, CURLOPT_URL, full_url);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postFields);

        // Perform the request and check for errors
        res = curl_easy_perform(curl);
        if(res != CURLE_OK)
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

        // Cleanup CURL resources
        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
    }
    curl_global_cleanup();
}


void join_session_c(const char* base_url, const char* session_id, const char* client_id) {
    CURL *curl;
    CURLcode res;
    char postFields[512]; // Adjust size as needed
    char full_url[1024];
    snprintf(full_url, sizeof(full_url), "%s/join_session", base_url);

    // Construct JSON payload
    sprintf(postFields, "{\"session_id\": \"%s\", \"client_id\": \"%s\"}", session_id, client_id);

    // Initialize CURL
    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();
    if(curl) {
        struct curl_slist *headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_URL, full_url);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postFields);

        // Perform the request
        res = curl_easy_perform(curl);
        if(res != CURLE_OK)
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

        // Cleanup
        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
    }
    curl_global_cleanup();
}
size_t write_callback_statuses(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t real_size = size * nmemb;
    printf("%s", (char*)contents);
    return real_size;
}

void get_all_session_statuses(const char* base_url) {
    CURL *curl;
    CURLcode res;
    char full_url[1024];
    snprintf(full_url, sizeof(full_url), "%s/list_sessions", base_url);

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, full_url);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback_statuses); // Use the callback to print the response

        // Perform the GET request
        res = curl_easy_perform(curl);
        if(res != CURLE_OK)
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

        curl_easy_cleanup(curl);
    }
    curl_global_cleanup();
}

size_t write_callback_flags(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t real_size = size * nmemb;
    printf("%s", (char*)contents);
    return real_size;
}

void get_flags(const char* base_url, const char* session_id) {
    CURL *curl;
    CURLcode res;
    char full_url[1024];
    snprintf(full_url, sizeof(full_url), "%s/get_flags?session_id=%s", base_url, session_id);

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, full_url);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback_flags); // Use the callback to print the response

        // Perform the GET request
        res = curl_easy_perform(curl);
        if(res != CURLE_OK)
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

        curl_easy_cleanup(curl);
    }
    curl_global_cleanup();
}

size_t variable_size_callback(char* ptr, size_t size, size_t nmemb, void* userdata) {
    size_t real_size = size * nmemb;
    char* found = strstr(ptr, "\"size\":");
    if (found) {
        int size = atoi(found + 7); // 7 characters to move past "\"size\":"
        *(int*)userdata = size;
    }
    return real_size;
}

int get_variable_size_c(const char* base_url, const char* session_id, int var_id) {
    CURL *curl;
    CURLcode res;
    char full_url[1024];
    int size = -1;  // Default to -1 to indicate failure or not found

    snprintf(full_url, sizeof(full_url), "%s/get_variable_size?session_id=%s&var_id=%d", base_url, session_id, var_id);

    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, full_url);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, variable_size_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &size);

        res = curl_easy_perform(curl);
        if(res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
    }

    return size;
}

int send_data_to_server(const char* base_url, const char* session_id, int var_id, const double* arr, int n) {
    CURL *curl;
    CURLcode res;
    struct curl_slist *headers = NULL;
    char full_url[1024];
    snprintf(full_url, sizeof(full_url), "%s/send_data", base_url);

    curl = curl_easy_init();
    if (!curl) {
        fprintf(stderr, "Failed to initialize curl\n");
        return -1;
    }

    char sessionHeader[256];
    char varHeader[256];
    
    // Prepare the headers
    snprintf(sessionHeader, sizeof(sessionHeader), "Session-ID: %s", session_id);
    snprintf(varHeader, sizeof(varHeader), "Var-ID: %d", var_id);

    headers = curl_slist_append(headers, "Content-Type: application/octet-stream");
    headers = curl_slist_append(headers, sessionHeader);
    headers = curl_slist_append(headers, varHeader);

    curl_easy_setopt(curl, CURLOPT_URL, full_url);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, arr);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, sizeof(double) * n);

    res = curl_easy_perform(curl);

    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);

    if (res != CURLE_OK) {
        fprintf(stderr, "Failed to send data: %s\n", curl_easy_strerror(res));
        return -1;
    }

    return 0;
}

size_t write_callback1(char* ptr, size_t size, size_t nmemb, void* userdata) {
    size_t total_size = size * nmemb;
    memcpy(userdata, ptr, total_size);
    return total_size;
}

// Function to fetch data from serve
int receive_data_from_server(const char* base_url, const char* session_id, int var_id, double* arr, int n) {
    CURL *curl;
    CURLcode res;
    struct curl_slist *headers = NULL;
    char fullUrl[512];  // Buffer for the full URL including query parameters

    // Construct the URL with query parameters
    snprintf(fullUrl, sizeof(fullUrl), "%s/receive_data?session_id=%s&var_id=%d", base_url, session_id, var_id);

    curl = curl_easy_init();
    if (!curl) {
        fprintf(stderr, "Failed to initialize curl\n");
        return -1;
    }

    // Set up the request with the full URL
    curl_easy_setopt(curl, CURLOPT_URL, fullUrl);

    // No need to set CURLOPT_HTTPHEADER for GET request query parameters
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback1);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, arr);

    // Perform the HTTP GET request
    res = curl_easy_perform(curl);

    // Cleanup
    curl_easy_cleanup(curl);

    if (res != CURLE_OK) {
        fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        return -1;
    }

    return 0;
}

void end_session_c(const char* base_url, const char* session_id, const char* client_id) {
    CURL *curl;
    CURLcode res;
    char postFields[512]; // Adjust size as needed
    char full_url[1024];
    snprintf(full_url, sizeof(full_url), "%s/end_session", base_url);
    
    // Construct the JSON payload
    snprintf(postFields, sizeof(postFields), "{\"session_id\": \"%s\", \"client_id\": \"%s\"}", session_id, client_id);
    
    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();
    if(curl) {
        struct curl_slist *headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_URL, full_url);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postFields);
        
        // Perform the request
        res = curl_easy_perform(curl);
        if(res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        } else {
            // Here you might want to handle the response.
            printf("Session ended successfully.\n");
        }
        
        // Clean up
        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
    }
    curl_global_cleanup();
}