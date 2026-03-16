
#define SDL_MAIN_USE_CALLBACKS 1  /* use the callbacks instead of main() */
#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
#include <string>
#include <iostream>
#include <array>
#include <map>
#include <utility>
#include <vector>
#include <chrono>
#include <unordered_map>
using namespace std;

/* We will use this renderer to draw into this window every frame. */
static SDL_Window* window = NULL;
static SDL_Renderer* renderer = NULL;
/* This function runs once at startup. */
SDL_AppResult SDL_AppInit(void** appstate, int argc, char* argv[])
{
    int i;
    SDL_SetAppMetadata("Example Renderer Primitives", "1.0", "com.example.renderer-primitives");
    if (!SDL_Init(SDL_INIT_VIDEO)) {
        SDL_Log("Couldn't initialize SDL: %s", SDL_GetError());
        return SDL_APP_FAILURE;
    }
    if (!SDL_CreateWindowAndRenderer("examples/renderer/primitives", 640, 480, SDL_WINDOW_RESIZABLE, &window, &renderer)) {
        SDL_Log("Couldn't create window/renderer: %s", SDL_GetError());
        return SDL_APP_FAILURE;
    }
    SDL_SetRenderLogicalPresentation(renderer, 640, 480, SDL_LOGICAL_PRESENTATION_LETTERBOX);
    return SDL_APP_CONTINUE;  /* carry on with the program! */
}

// --------------------------- CUBE SETUP
int cubeSize = 25;
int uOffset = (cubeSize * 3, cubeSize * 0);
int lOffset = (cubeSize * 0, cubeSize * 3);
int fOffset = (cubeSize * 3, cubeSize * 3);
int rOffset = (cubeSize * 6, cubeSize * 3);
int bOffset = (cubeSize * 9, cubeSize * 3);
int dOffset = (cubeSize * 3, cubeSize * 6);

map<char, array<int, 3>> colorMap = {
    {'U', {255, 255, 255}}, // White
    {'L', {255, 165, 0}},   // Orange
    {'F', {0, 255, 0}},     // Green
    {'R', {255, 0, 0}},     // Red
    {'B', {0, 0, 255}},     // Blue
    {'D', {255, 255, 0}}    // Yellow
};
// Face offsets in the 3x3 net layout (xOffset, yOffset)
array<pair<int, int>, 6> faceOffsets = { {
    {3, 0}, // U
    {0, 3}, // L
    {3, 3}, // F
    {6, 3}, // R
    {9, 3}, // B
    {3, 6}  // D
} };

using Move = array<array<uint8_t, 2>, 21>;
unordered_map<string, Move> fMoves = {
    {"U",  {{{0,2},{1,5},{2,8},{3,1},{4,4},{5,7},{6,0},{7,3},{8,6},{29,20},{28,19},{27,18},{9,36},{10,37},{11,38},{18,9},{19,10},{20,11},{38,29},{37,28},{36,27}}}},
    {"D",  {{{51,45},{52,48},{53,51},{48,46},{49,49},{50,52},{45,47},{46,50},{47,53},{35,44},{34,43},{33,42},{15,24},{16,25},{17,26},{24,33},{25,34},{26,35},{44,17},{43,16},{42,15}}}},
    {"L",  {{{0,18},{3,21},{6,24},{51,38},{48,41},{45,44},{15,9},{12,10},{9,11},{16,12},{13,13},{10,14},{17,15},{14,16},{11,17},{24,51},{21,48},{18,45},{44,0},{41,3},{38,6}}}},
    {"R",  {{{2,42},{5,39},{8,36},{53,26},{50,23},{47,20},{35,33},{32,34},{29,35},{34,30},{31,31},{28,32},{33,27},{30,28},{27,29},{26,8},{23,5},{20,2},{42,47},{39,50},{36,53}}}},
    {"F",  {{{6,27},{7,30},{8,33},{45,11},{46,14},{47,17},{33,45},{30,46},{27,47},{17,6},{14,7},{11,8},{24,18},{25,21},{26,24},{21,19},{22,22},{23,25},{18,20},{19,23},{20,26}}}},
    {"B",  {{{0,15},{1,12},{2,9},{51,35},{52,32},{53,29},{35,2},{32,1},{29,0},{15,53},{12,52},{9,51},{44,42},{43,39},{42,36},{41,43},{40,40},{39,37},{38,44},{37,41},{36,38}}}},
    {"U'", {{{0,6},{1,3},{2,0},{3,7},{4,4},{5,1},{6,8},{7,5},{8,2},{29,38},{28,37},{27,36},{9,18},{10,19},{11,20},{18,27},{19,28},{20,29},{38,11},{37,10},{36,9}}}},
    {"D'", {{{51,53},{52,50},{53,47},{48,52},{49,49},{50,46},{45,51},{46,48},{47,45},{35,26},{34,25},{33,24},{15,42},{16,43},{17,44},{24,15},{25,16},{26,17},{44,35},{43,34},{42,33}}}},
    {"L'", {{{0,44},{3,41},{6,38},{51,24},{48,21},{45,18},{15,17},{12,16},{9,15},{16,14},{13,13},{10,12},{17,11},{14,10},{11,9},{24,6},{21,3},{18,0},{44,45},{41,48},{38,51}}}},
    {"R'", {{{2,20},{5,23},{8,26},{53,36},{50,39},{47,42},{35,29},{32,28},{29,27},{34,32},{31,31},{28,30},{33,35},{30,34},{27,33},{26,53},{23,50},{20,47},{42,2},{39,5},{36,8}}}},
    {"F'", {{{6,17},{7,14},{8,11},{45,33},{46,30},{47,27},{33,8},{30,7},{27,6},{17,47},{14,46},{11,45},{24,26},{25,23},{26,20},{21,25},{22,22},{23,19},{18,24},{19,21},{20,18}}}},
    {"B'", {{{0,29},{1,32},{2,35},{51,9},{52,12},{53,15},{35,51},{32,52},{29,53},{15,0},{12,1},{9,2},{44,38},{43,41},{42,44},{41,37},{40,40},{39,43},{38,36},{37,39},{36,42}}}},
    {"U2", {{{0,8},{1,7},{2,6},{3,5},{4,4},{5,3},{6,2},{7,1},{8,0},{29,11},{28,10},{27,9},{9,27},{10,28},{11,29},{18,36},{19,37},{20,38},{38,20},{37,19},{36,18}}}},
    {"D2", {{{51,47},{52,46},{53,45},{48,50},{49,49},{50,48},{45,53},{46,52},{47,51},{35,17},{34,16},{33,15},{15,33},{16,34},{17,35},{24,42},{25,43},{26,44},{44,26},{43,25},{42,24}}}},
    {"L2", {{{0,45},{3,48},{6,51},{51,6},{48,3},{45,0},{15,11},{12,14},{9,17},{16,10},{13,13},{10,16},{17,9},{14,12},{11,15},{24,38},{21,41},{18,44},{44,18},{41,21},{38,24}}}},
    {"R2", {{{2,47},{5,50},{8,53},{53,8},{50,5},{47,2},{35,27},{32,30},{29,33},{34,28},{31,31},{28,34},{33,29},{30,32},{27,35},{26,36},{23,39},{20,42},{42,20},{39,23},{36,26}}}},
    {"F2", {{{6,47},{7,46},{8,45},{45,8},{46,7},{47,6},{33,11},{30,14},{27,17},{17,27},{14,30},{11,33},{24,20},{25,19},{26,18},{21,23},{22,22},{23,21},{18,26},{19,25},{20,24}}}},
    {"B2", {{{0,53},{1,52},{2,51},{51,2},{52,1},{53,0},{35,9},{32,12},{29,15},{15,29},{12,32},{9,35},{44,36},{43,37},{42,38},{41,39},{40,40},{39,41},{38,42},{37,43},{36,44}}}}
};

vector<const Move*> movePtrs = {
    &fMoves.at("U")
};

using Cube = array<char, 54>;
Cube solvedCube = { 'U','U','U','U','U','U','U','U','U',
                    'L','L','L','L','L','L','L','L','L',
                    'F','F','F','F','F','F','F','F','F',
                    'R','R','R','R','R','R','R','R','R',
                    'B','B','B','B','B','B','B','B','B',
                    'D','D','D','D','D','D','D','D','D'};


inline void applyMove(Cube& cube, const Move& move) noexcept {
    char temp[21];
    #pragma unroll
    for (int i = 0; i < 21; ++i)
        temp[i] = cube[move[i][0]];
    #pragma unroll
    for (int i = 0; i < 21; ++i)
        cube[move[i][1]] = temp[i];
}

inline void applyMoves(Cube& cube, const vector<const Move*>& movePtrs) noexcept {
    for (const Move* m : movePtrs)
        applyMove(cube, *m);
}

static void drawCube(Cube& cubeState)
{
    SDL_FRect rect;
    SDL_FRect outLine;
    for (int i = 0; i < (int)cubeState.size(); ++i) {
        char face = cubeState[i];
        int faceIndex = i / 9;         // Which face (0–5)
        int pos = i % 9;               // Which sticker (0–8)
        int xOff = faceOffsets[faceIndex].first;
        int yOff = faceOffsets[faceIndex].second;
        rect.x = outLine.x = cubeSize * (xOff + (pos % 3));
        rect.y = outLine.y = cubeSize * (yOff + (pos / 3));
        rect.w = rect.h = outLine.w = outLine.h = cubeSize;
        auto color = colorMap[face];

        SDL_SetRenderDrawColor(renderer, color[0], color[1], color[2], SDL_ALPHA_OPAQUE);
        SDL_RenderFillRect(renderer, &rect);

        SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE);
        SDL_RenderRect(renderer, &outLine);
    }
}


/* This function runs when a new event (mouse input, keypresses, etc) occurs. */
SDL_AppResult SDL_AppEvent(void* appstate, SDL_Event* event)
{
    if (event->type == SDL_EVENT_QUIT) {
        return SDL_APP_SUCCESS;  /* end the program, reporting success to the OS. */
    }
    if (event->type == SDL_EVENT_KEY_DOWN) {
        /* the pressed key was Escape? */
        if (event->key.key == SDLK_S) {
            cout << "Solve" << endl;
        }
        if (event->key.key == SDLK_U) {
            cout << "umove" << endl;
            applyMove(solvedCube, fMoves["U"]);
        }
        if (event->key.key == SDLK_T) {
            cout << "Test" << endl;

			auto start = chrono::high_resolution_clock::now();
            for (int i = 0; i < 100000; ++i) {
                applyMoves(solvedCube, movePtrs);
            }
			auto end = chrono::high_resolution_clock::now();

			chrono::duration<double, std::milli> elapsed = end - start;
			double rate = (100000 / elapsed.count()) * 1000.0;
			cout << "100,026 moves in " << elapsed.count() << "ms " << rate / 1000000 << "million moves/second" << endl;
        }
    }
    return SDL_APP_CONTINUE;  /* carry on with the program! */
}


/* This function runs once per frame, and is the heart of the program. */
SDL_AppResult SDL_AppIterate(void* appstate)
{
    SDL_FRect rect;

    /* as you can see from this, rendering draws over whatever was drawn before it. */
    SDL_SetRenderDrawColor(renderer, 33, 33, 33, SDL_ALPHA_OPAQUE);  /* dark gray, full alpha */
    SDL_RenderClear(renderer);  /* start with a blank canvas. */

    drawCube(solvedCube);

    SDL_RenderPresent(renderer);  /* put it all on the screen! */
    return SDL_APP_CONTINUE;  /* carry on with the program! */
}

/* This function runs once at shutdown. */
void SDL_AppQuit(void* appstate, SDL_AppResult result)
{
    /* SDL will clean up the window/renderer for us. */
}


