# Supervisor comments restored with replies (V8)

The comments of the 2026-08-11 round (C1-C13) and the 2026-08-31
Chapter 3 round (C15-C21), restored as threaded Word comments in
Thesis_V8_commented.docx, each with a reply stating what changed.
The anchor column is where the comment sits in the built text, for
adding the same threads to an online copy.

## 1. (C1) anchored at: "Examining Committee:"
- **Comment (S.P.):** The title page should follow the format of the thesis template. There should be other members listed. I do not see the name of other committee members.
- **Reply (L.L.):** Rebuilt the title and approval pages in the template order and added the committee block. The other members' names are marked placeholders until I can confirm them with you.

## 2. (C2) anchored at: "This thesis develops a system that tracks a person's upper body"
- **Comment (S.P.):** The abstract needs to be rewritten more aligned with your language. Also, make sure you mention that the tracking results are compared with the ground truth which is the actual path you define in the lab.
- **Reply (L.L.):** Rewrote the abstract in my own words. It now says the path defined in the laboratory is the ground truth and the tracked trajectory is compared against it.

## 3. (C3) anchored at: "A thesis submitted in partial fulfillment"
- **Comment (S.P.):** Make each chapter starts on a new page. Make sure you follow the eng. Sci thesis format template.
- **Reply (L.L.):** Every chapter, the references and each appendix now start on a new page, and the whole file runs on one font set per the template.

## 4. (C4) anchored at: "shows the layout in a photograph taken from above the desk"
- **Comment (S.P.):** In chapter 2, first show the image of the whole setup using your phone. This should include the ground truth wire that the person need to follow, the Aruco markers, the RGB-D sensor and you. This should come first before other images and explain the overall objective of the user study.
- **Reply (L.L.):** The whole-setup photo now opens Chapter 2 as Figure 2.1, with the study objective stated beside it. I still owe you a retake that also has the sensor and me in the frame.

## 5. (C5) anchored at: "Averaging the ten translations is a plain arithmetic mean"
- **Comment (S.P.):** Somehow the equations in the Word file is messed up. Equations in section 4.2.1 are not showing correctly.
- **Reply (L.L.):** The equations are rebuilt as native Word math throughout. Please tell me if any still look broken in your Word and I will switch that section to rendered images.

## 6. (C6) anchored at: "The pipeline therefore handles each case in a separate stage"
- **Comment (S.P.):** When you talk about data filtering, you need to mention which one you have used and why. Then, refer the reader to a reference textbook (or wherever you have borrowed them from). You should also show the results after filtering.
- **Reply (L.L.):** Section 2.5 now names each filter used, why it is chosen, and its textbook reference, and shows a before and after figure for every stage.

## 7. (C7) anchored at: "Appendix F compares the candidate smoothers side by side"
- **Comment (S.P.):** Not sure if we should add an appendix highlighting the features of each filter.
- **Reply (L.L.):** I drafted Appendix F with the candidate filters side by side. It is a single deletion if you would rather leave it out.

## 8. (C8) anchored at: "shows the test flagging a wrist spike"
- **Comment (S.P.):** Figure 2.5 is not clear. You may want to break it down to make a bigger. Also label the Figures and add captions for each set.
- **Reply (L.L.):** The combined panel is now three separate larger figures, one per stage, each labelled and captioned.

## 9. (C9) anchored at: "The arm model borrows its shape from robotics"
- **Comment (S.P.):** In the joint angle calculation section, show a kinematic model of an arm (similar to what we draw in robotics course) and the label which joint angle is which. This clear figure should come before section 3.4.1. For example, draw some schematic similar to PUMA robot for the shoulder joint and connected elbow joint and the wrist point. In there, label the joints which you are solving for.
- **Reply (L.L.):** Added Section 3.3.1 before the angle computation: Figure 3.6 gives the standard seven-degree-of-freedom description with its PUMA-style chain, and Figure 3.7 draws the four solved joints on the body with every angle labelled.

## 10. (C10) anchored at: "The wrist is not a solved joint of this model"
- **Comment (S.P.):** Section 3.4.4, we do not solve for wrist joints. We are solving for the shoulder and elbow joints. The wrist would be just a 3D point which we can then track.
- **Reply (L.L.):** Section 3.4.4 is retitled The Wrist as a Tracked Point and now presents the wrist exactly that way.

## 11. (C11) anchored at: "A single measured frame now carries the whole chain"
- **Comment (S.P.):** In the example you are solving, you need to directly refer to the kinematic diagram of PUMA type model which I mention above and show the corresponding angles that you are solving for.
- **Reply (L.L.):** The worked example now points every solved value at its label in the schematic at the step where it is solved.

## 12. (C12) anchored at: "The rotation obtained that way is called the chordal mean"
- **Comment (S.P.):** What is chordal-mean anchor?
- **Reply (L.L.):** Defined it here at first use: the element-wise mean of the calibration rotations projected back onto the nearest proper rotation, then frozen as the anchor.

## 13. (C13) anchored at: "[UPDATE FIELDS IN WORD: F9]"
- **Comment (S.P.):** Prepare the table of content of the thesis as we have agreed and based on the thesis format. Sent it to me so we can call it finalized.
- **Reply (L.L.):** This is the finalized structure we agreed on. The contents and list pages are self-updating Word fields; pressing F9 fills in the page numbers.

## 14. (C15) anchored at: "The two combine into one representation, the 4 by 4 homogeneous transformation matrix T"
- **Comment (S.P.):** You should also show the T matrix which combines both R and t in one representation. For example, equation 3.2 is valid when the origin of both child and parent are the same location. You should show the corresponding T matrix here as well.
- **Reply (L.L.):** Equation (3.2) now shows T with R and t as blocks and its action on a point. The rotation-only mapping is scoped to directions and shared origins, with the inverse T form beside it in equation (3.4).

## 15. (C16) anchored at: "Each neighbouring pair of frames"
- **Comment (S.P.):** Referring to Figure 3.3, you should also define the T matrices between the various frames. For example, T of the shoulder about the root (torso) frame, elbow with respect to the shoulder and .. This makes it clear that each frame is different from the other in terms of relative rotation and position of their origin.
- **Reply (L.L.):** Equation (3.5) now defines the three T matrices of the chain right after the chain figure, each with its own rotation and origin, and equation (3.6) composes them.

## 16. (C17) anchored at: "These relative transformations are the plan of the whole chapter"
- **Comment (S.P.):** Then it is clear when you mention that when you measure the landmark position of say the shoulder with respect to the sensor frame, you can use these relative T matrices to obtain for example, the position of the shoulder landmark with respect to the torso (root frame). As you have it, you do not make this clear in explaining the logic before you go over the details.
- **Reply (L.L.):** Added this logic paragraph before any construction: each landmark is measured with respect to the sensor and the inverse T matrices carry it into the frame where its joint is solved.

## 17. (C18) anchored at: "the first transformation announced in equation"
- **Comment (S.P.):** Same for equation 3.7. You should define the T matrix here as well which defines the relative position and orientation of the root frame with respect to the sensor frame.
- **Reply (L.L.):** Equation (3.12) now shows the root T matrix right where the rotation and origin are assembled.

## 18. (C19) anchored at: "this fills in the second transformation"
- **Comment (S.P.):** Same goes in the section about the shoulder T matrix with respect to the root.
- **Reply (L.L.):** Equations (3.13) and (3.14) define the shoulder and elbow T matrices in the section that places those frames.

## 19. (C20) anchored at: "Appending the origin"
- **Comment (S.P.):** Then in the numerical section, you should show how each of these T matrices look like.
- **Reply (L.L.):** The worked example now prints all three T matrices as numbers and closes with the chain check: their product lands exactly on the measured elbow.

## 20. (C21) anchored at: "Figure 3.1 draws the information flow"
- **Comment (S.P.):** I also think that at the beginning of this chapter, you should draw a visual information flow diagram. This way, the reader can clearly see how each sections come together. For example, you have raw/calibrated information from the landmarks of torso and arms coming in. The torso landmark are used to establish the T matrix of the torso frame with respect to the sensor frame. ... So use AI tools to create this visual data flow where the reader can then get a better idea of the process.
- **Reply (L.L.):** Figure 3.1 is the new information-flow diagram at the start of the chapter. Each box names the section that builds it and the arrows carry the T matrices between the stages.

## 21. (C43) anchored at: "The preprocessing writes a separate output and never modifies the raw data"
- **Comment (S.P.):** You should mention how the signal filtering of this chapter (section 2.4 (I think you should call it measurement filtering or something like this).
- **Reply (L.L.):** Renamed the section Measurement Filtering, now Section 2.5. Its closing sentences say where the filtered signals go: the landmarks into the joint-angle solve of Chapter 3 and the object track into Chapter 4.

## 22. (C44) anchored at: "The pipeline uses only a subset of MediaPipe's output"
- **Comment (S.P.):** I also think you should use AI again for clarity BUT keeping your level of English and vocabulary.
- **Reply (L.L.):** Kept my own wording throughout the chapter. I only split a few long sentences, and the new frames section is written in the same plain style.

## 23. (C45) anchored at: "draws the frames of the scene on one colour frame of the recording"
- **Comment (S.P.):** Also, what is missing is the overall picture of the subject, the table, the markers and the wall. You need to draw the main coordinates involves in your setup. ... For example, draw a frame on each of the Aruco markers. Draw the World frame on the wall aruco marker. Show the sensor frame. Then draw arrows between the frame corresponding the T matrices and so on.
- **Reply (L.L.):** Figure 2.5 now draws a frame on each marker, the sensor frame, and arrows for the T matrices between them. I kept the world frame on the desk marker rather than the wall marker, because it lies on the tabletop where the object moves; the wall marker gives the vertical.

## 24. (C46) anchored at: "Every measurement in this thesis is a position or an orientation"
- **Comment (S.P.):** Also, include the calibration section here as well. Define the coordinate frames here and the overall T matrices between the frame (just the notation). Just like Chapter 2 of your robotics book.
- **Reply (L.L.):** Section 2.2 now defines every frame of the thesis and names the T matrices between them, and the scene calibration moved here from Chapter 4. Chapters 3 and 4 refer back to it.

## 25. (C22) anchored at: "It sits between the filtering of Chapter 2 and the solve of Chapter 3"
- **Comment (S.P.):** One general comment. You can ask AI tool to revise it but keep the style and English similar. The write-up does not read smooth.
- **Reply (L.L.):** I redrafted the whole chapter in shorter and plainer sentences and kept the equations and figures. The torso repair section is out, since the chapter now assumes the torso is measured on every frame, as we discussed.

## 26. (C23) anchored at: "Figure 5.3 draws the two equations"
- **Comment (S.P.):** Also, add a simple schematic when you are explaining equations 5.1 and 5.2
- **Reply (L.L.):** Figure 5.3 now sits right under equation (5.2). Panel (a) reads the offset off a clean frame and panel (b) carries it to a later frame where the wrist is hidden.

## 27. (C24) anchored at: "Table 5.1 lists every symbol the chapter uses"
- **Comment (S.P.):** You should also define all the variables which you used in this chapter if they are not defined before.
- **Reply (L.L.):** Table 5.1 lists every symbol of the chapter with its frame and where it comes from, and each symbol is also defined at first use. Symbols that had two meanings are renamed.

## 28. (C25) anchored at: "That offset is not known in general"
- **Comment (S.P.):** Remember, when we comparing the track data with the ground truth, we compare the trajectory of the Aruco marker on the object which is being handled and the position of the writs points of the two hands (knowing there will be an offset of where the object aruco marker is and where the writs point is. Although for example you can assume some h, but in general, we will not know. Hence, by comparing with the ground truth, we can have some sense of how far away tracked and reconstructed data are with respect to the ground truth.
- **Reply (L.L.):** Section 5.3 now says that the wrist is not on the marker, that the offset h is not known in general, and that I estimate it from the clean frames of each grasp. Chapter 7 compares the wrist and the marker trajectories with the reference path.

## 29. (C26) anchored at: "The chapter covers three cases."
- **Comment (S.P.):** Also, I am not sure how this chapter (beside saying that you have various missing data cases) will fit previous chapters. For example, in previous chapters we track the Aruco marker on the object and we can compare it with the ground truth. Then, we use the kinematic model of the arms based on the measured landmarks to compute the position of the wrist. It is not clear for example, if the writs landmark is missing, can we estimate where the writs can be using the kinematic model of the elbow and shoulder.
- **Reply (L.L.):** The opening now lists the three missing-data cases in the words of the Chapter 3 chain. The case you ask about is Case A: the wrist is placed at the forearm length from the elbow along the remembered forearm direction, equation (5.6).

## 30. (C27) anchored at: "Figure 5.1 draws the information flow of the chapter"
- **Comment (S.P.):** Perhapse you want to add some sort of information pipeline flow diagram at the begineeing of how the estimation part of this chapter is used within the models presented in the previous chapter.
- **Reply (L.L.):** Figure 5.1 is the new information-flow diagram at the start of the chapter, with the inputs from Chapters 2 to 4 on the left and the outputs to Chapters 6 and 7 on the right.

## 31. (C28) anchored at: "The recovery needs parameters of three kinds"
- **Comment (S.P.):** Also state a clear assumptions about what parameters you need (e.g. h) in order for this estimation to work properly and how in collected data experiments, this parameters is obtained.
- **Reply (L.L.):** Section 5.1 states the assumptions in plain sentences and names the parameters in three kinds, calibrated constants, design values and fitted states; each value is stated where its equation or rule is introduced, and no parameter is fitted on a flagged frame.

## 32. (C48) anchored at: "Averaging the ten desk rotations of the calibration window element by element gives"
- **Comment (S.P.):** In the value of the matrices, do not go beyond two decimals. For example, if it is 0.0014 just write 0.0. Same comments for all the numerical values.
- **Reply (L.L.):** Every printed number in the thesis now stops at two decimals, matrices and vectors included, and the appendices follow the same rule. Where rounding would break a displayed calculation I dropped the intermediate step and kept the result.

## 33. (C49) anchored at: "shows the object marker as the camera sees it at four moments of the task"
- **Comment (S.P.):** It would be nice if you can show the images of the experiment.
- **Reply (L.L.):** Added Figure 4.1: four camera frames of the task, from the grasp on the desk to the far end of the rail, with the detected marker outlined and its axes drawn on each, plus the world frame on the desk marker.

## 34. (C50) anchored at: "The rail task of Section 7.1 uses one hand"
- **Comment (S.P.):** Can you add the second arm in the wooden block experiment. I mean, one arm slide the object half way and then the other arm grasp the object half way and continue. Even if it is filled with error, you should show them. If it can not be done, then forget it. We use the later results you have presented. I just want to show the results as closely related to the theme of your thesis and its title.
- **Reply (L.L.):** I recorded the rail task again with the handover you describe and added it as Section 7.7, with the errors as they came out: the right hand slides the cube 30 cm, both hands hold it for 5 s, the left hand slides the rest. The cube stays within 1.7 cm of the rail line through the handover, and the section shows what the hands in front of the hips do to the torso.

## 35. (C51) anchored at: "The difficulties lie in the sensing."
- **Comment (S.P.):** Rewrite the abstract. Basically abstract wants to state a) what is the problem and why doing it; b) what are the challenges; d) how you have addressed them and e) how you solve it and what you have accomplished.
- **Reply (L.L.):** The abstract now has four paragraphs in that order: the problem and why, the challenges, how I addressed them, and what was accomplished, with the same numbers as before.

## 36. (C52) anchored at: "This chapter reads the results of Chapters 7 and 8 against the sensing and the model"
- **Comment (S.P.):** I think it is better to have a chapter called discussions since there are a lot to discuss about all your results.
- **Reply (L.L.):** Chapter 9 is now the discussion, one section per result: the object track against the rail, the arm pose and the recovery, the handover, the torso, the landmark failures, the live structure, and the limits with Table 9.1.

## 37. (C53) anchored at: "This chapter answers the objectives of Chapter 1 from the results of Chapters 7 to 9"
- **Comment (S.P.):** Add another chapter called, Conclusions and Future work.
- **Reply (L.L.):** Chapter 10 holds the conclusions, answering the five objectives in order, and the future work.
