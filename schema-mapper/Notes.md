# Choosing models

# Refining prompts
### Different attempts
#### V0 Models and prompts
This was a wave of different attempts I made to get the data to condition correctly. I went through a number of different models to determine how I could approach the problem.

In my initial solutioning, I was learning about models. I learned a lot about specifically
- Model sizes: What the different options for model sizes are in terms of number of parameters
- Quantization: What quantization is and how it affects model size and the quality of the output
- Types of models: I originally used a variety of different models to try and find the right model for the job. I tried with general purpose models, instruction oriented models, coding models, and creative models. These distintions, I learned, are important in completing your task.
- How to run models locally: I can use tools like ollama to run locally on my desktop
- Running on CPU vs GPU: I learned how model size relates to the ability to run on GPU vs spilling over to CPU, and the speed difference as well. I am using a NVIDIA 3070 Ti for local execution at home with 8GB total of VRAM.
- How to prompt the model correctly: I had experimented with so many ways to prompt the model. It was a compination of factors that ultimately lead to my success, but there was a large amount of time spent debugging and figuring out how can this model do what I want it to? I first gave it a task, but saw that there was a lot of summarization going on. I then worked to try to avoid that summarization at all costs, without truly landing on a good prompt. After much debugging, I thought, "What's the simplest thing I can ask the model to do?" So I went down the route of trying to get it to inject line break indicators and even return back the first location in the text where a line break would occur. Since the model sizes were small, this yielded poor results. At this stage I almost gave up, but I saw how, if I asked chatgpt+ to do the same prompt, it could fulfill this request accurately. I persisted and thought that there must be a way. A glimmer of hope shown as I tried the 70B model of llama 3.1 on my machine (albeit very processing very slowly since I didn't have the VRAM to support it).

#### V1 Model and prompt
I received some absolutely thrilling results for some of my files when I moved up to 70B parameters. This was still quantized, but I saw 99%+ accuracy in terms of translating the files. With this encouragement, I built out a pipeline on lambda cloud for processing files more quickly (it would have taken years of compute if it had been done just on CPU).

Setting up on llamda cloud was a relatively smooth process. There was a lot of exploration in specs and anticipated output vs cost. Originally, I thought to run this on a PCIe H100 instance, but saw that there were cheaper options for GH200, which looked like, on paper, it might yeild similar performance.

After some initial environment settup snafu - mainly I encountered that the lambda ai cloud instances had issues communicating with other machines. Running file transfer using the recommended tools yielded issues, even after terminating my original instance and starting a new one afresh. I encountered networking issues where lots of requests would not go through. This could have been due to DNS issues or something else. The main symptom I saw were requests timing out. If a request didn't succeed (i.e. file transfer, or download repo from git, or download ollama) in the first few seconds, it would likely time out. This was a bit annoying, but I guess for insanely cheap compute, this is to be expected; you get what you pay for.

After the environment was settup, and my batch execution scripts were in place, I ran execution. I saw the 70B model have good performance, max out 1 CPU and then max out the GPU compute, while being under in GPU VRAM. This was all good. I saw a processing speed of roughly 37 tokens per second. 

This speed for processing was ok, but I calculated that it would have taken over 300 hours to process 6,300 talks, which would have been a lot of money. So I stopped the execution flow and came back to the problem. I messed around with context windows, and grouped the files by max approximate token size in order to hopefully run the model with a few passes, with varying context windows so that it would more efficiently process all of the fils. I did see an improvement, but it was on the magnitude of approximately 1 token/second. Not really worth it...

I was also interested in checking the accuracy of the output. Surprisingly, it was very underwhelming... The original files, which I ran locally, amazingly all had great accuracy. But in my larger dataset, I still saw a lot of summarization, content deletion, etc. I verified these locally and saw the same poor behavior for these particular files.

This is where I shifted focus to 8B models, after many indicators in my research that 8B is actually fine for just structuring data. As other sections of this note document indicate, this is actually the case.

#### V2 Models and beyond
This is where I'm at currently. I'm refining my model prompt to have more accurate output. 

The plan forward is trying to improve the model accuracy. I'm not sure if I'll ever be able to land on a single prompt that works for all transcription files, so another option is to have multiple model files, and take passes at the data. If model A doesn't work, try model B. If model B works, we don't need to try model C and we can remove it from further waves of processing.

## Overconditioning
Overconditioning happens when you give too much input to a model. These LLM's are trained on large datasets. When we give it too many instructions, it may interpret this prompt as a different intent than the one we think we're asking for. 

It's interesting because this intent is a result of latent behavior. The models are trained on sets of data, input and output. If your input and output that you asked for starts to look more like this other input/output pattern, the model is going to respond to that other ouput pattern. My intent for it was to structure the data, but it would often jump into content editor or summarizer. 

This outlines why the prompts are so important. Finding the sweet spot between too little info and too much info for what you're trying to accomplish is very difficult. ChatGPT and other companies know this, and so each query is actually run through a number of models. They do some more processing on their end to match your intent and expected output, and filter out a lot of results before it ever gets to the user if the output is off. However, in a local, single model world, this isn't so straightforward.

## Right-sizing
For pure structuring of data,llama 3.1 - with Q4_K_M parameterization is totally fine. This is a simple task that does not require much specialty.

The benefits of larger models is that they've seen more data. They're more experienced in different types of workstreams, like content editing, and so can respond to your jobs appropriately. However, this can be overkill, especially if all you want is content structuring. You get a lot slower execution and not necessarily better output.

When it comes to later stages of data processing, larger models can shine for more complex tasks. In example, if a later part of the processing stage involves correcting specialty terminology that might have been misinterpreted by an ASR (Automatic Speech Recognition) system, then a larger model can correct these terminologies. Smaller models may not have much familiarity with specialty terms or names

Smaller models run much faster, but haven't seen nearly as much of world as larger models. This makes them efficient at a set of simple tasks, but it can be impossible to do more complicated tasks.

## Processing stages
One theme of overconditioning is that you can't give the model too much to do, otherwise it will reclasify your intent and give output you weren't expecting. Given that executing models can be an expensive task, this can be frustrating because one might want to run everything once, and have it all magically be processed according to the intent. However, as described before, this is likely to not be possible.

Given the task of cleaning up ASR transcripts, it's thus necessary to take multiple passes at it. The first pass for structuring the data properly, another pass for fixing terminology, perhaps another pass for fixing just names (I have yet to do the terminology and name fixing stages). 

The benefit of doing multiple passes, though, is that you can measure accuracy at each pass for well defined stages. For content structuring, I've implemented a check wiht the python SequenceMatcher library that tells me how true is the model output to the original input. This lets me discretely judge how much the model added, removed, modified, or summarized. This is very useful in measuring the effectiveness of the prompts I'm creating as well as the pipeline as a whole.

Stage-by-stage validation lets you program high quality checks to ensure the model intent is being followed truthfully, and verifies your faith in the model.

### Results
Between my v1 prompt running on ollama 3.1 70B parameter, and the 8B parameter, I actually saw a higher accuracy with the refined prompt on the 8B model.

```
V1 70B parameter - 90% likeness threshold
Entries: 77
Successes: 10
Success rate: 0.1299
Average likeness: 0.4760
Median likeness: 0.5399

V1 70B parameter - 95% likeness threshold

Entries: 77
Successes: 7
Success rate: 0.0909
Average likeness: 0.4760
Median likeness: 0.5399

---

V2 8B parameter - 90% likeness threshold
Entries: 56
Successes: 19
Success rate: 0.3393
Average likeness: 0.7843
Median likeness: 0.8117

V2 8B parameter - 95% likeness threshold
Entries: 56
Successes: 11
Success rate: 0.1964
Average likeness: 0.7843
Median likeness: 0.8117
```

### Result Interpretation
This shows that the size of the model is not the limiting factor here. See other sections for considerations on why you might not want to use a larger model for simple tasks such as these.