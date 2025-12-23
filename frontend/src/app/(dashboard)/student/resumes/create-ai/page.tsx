/**
 * =============================================================================
 * AI RESUME BUILDER - 🔥 MOST IMPORTANT PAGE
 * =============================================================================
 *
 * Features:
 * - Split screen: Left 40% Form, Right 60% Live Preview
 * - Multi-step form (Personal Info, Experience, Education, Skills, Additional)
 * - AI generation with template/tone selection
 * - Real-time preview with template switcher
 * - Auto-save, progress bar, validation
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
import {
  Sparkles,
  User,
  Briefcase,
  GraduationCap,
  Code,
  Award,
  ArrowRight,
  ArrowLeft,
  Plus,
  Trash2,
  Mail,
  Phone,
  MapPin,
  Linkedin,
  Globe,
  Loader2,
  CheckCircle,
  Download,
  ZoomIn,
  ZoomOut,
  FileText,
  Eye,
  Save,
  Wand2,
  Palette,
  Type,
  RotateCcw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

// =============================================================================
// TYPES & SCHEMAS
// =============================================================================

const personalInfoSchema = z.object({
  fullName: z.string().min(2, "Name is required"),
  email: z.string().email("Valid email required"),
  phone: z.string().min(9, "Phone is required"),
  location: z.string().optional(),
  professionalTitle: z.string().min(2, "Professional title is required"),
  linkedinUrl: z.string().url().optional().or(z.literal("")),
  portfolioUrl: z.string().url().optional().or(z.literal("")),
});

const experienceSchema = z.object({
  experiences: z.array(
    z.object({
      company: z.string().min(1, "Company name is required"),
      position: z.string().min(1, "Position is required"),
      startDate: z.string().min(1, "Start date is required"),
      endDate: z.string().optional(),
      isCurrent: z.boolean().optional(),
      description: z.string().min(10, "Description is required"),
    })
  ),
});

const educationSchema = z.object({
  education: z.array(
    z.object({
      institution: z.string().min(1, "Institution is required"),
      degree: z.string().min(1, "Degree is required"),
      field: z.string().min(1, "Field is required"),
      year: z.string().min(1, "Year is required"),
    })
  ),
});

const skillsSchema = z.object({
  technicalSkills: z.array(z.string()),
  softSkills: z.array(z.string()),
  languages: z.array(
    z.object({
      name: z.string(),
      proficiency: z.string(),
    })
  ),
});

const additionalSchema = z.object({
  certifications: z.array(
    z.object({
      name: z.string(),
      issuer: z.string(),
      year: z.string(),
    })
  ),
  projects: z.array(
    z.object({
      name: z.string(),
      description: z.string(),
      url: z.string().optional(),
    })
  ),
});

// Combined schema
const resumeSchema = personalInfoSchema
  .merge(experienceSchema)
  .merge(educationSchema)
  .merge(skillsSchema)
  .merge(additionalSchema);

type ResumeFormData = z.infer<typeof resumeSchema>;

// =============================================================================
// STEP CONFIGURATION
// =============================================================================

const steps = [
  { id: 1, title: "Personal Info", icon: User, description: "Basic contact details" },
  { id: 2, title: "Experience", icon: Briefcase, description: "Work history" },
  { id: 3, title: "Education", icon: GraduationCap, description: "Academic background" },
  { id: 4, title: "Skills", icon: Code, description: "Your expertise" },
  { id: 5, title: "Additional", icon: Award, description: "Extra sections" },
];

const templates = [
  { id: "modern", name: "Modern", description: "Clean, contemporary design" },
  { id: "classic", name: "Classic", description: "Traditional professional" },
  { id: "minimal", name: "Minimal", description: "Simple and elegant" },
  { id: "creative", name: "Creative", description: "Stand out from the crowd" },
];

const tones = [
  { id: "professional", name: "Professional", description: "Formal and corporate" },
  { id: "confident", name: "Confident", description: "Bold and assertive" },
  { id: "friendly", name: "Friendly", description: "Warm and approachable" },
  { id: "technical", name: "Technical", description: "Detail-oriented" },
];

const commonSkills = {
  technical: [
    "JavaScript", "TypeScript", "Python", "React", "Node.js", "PostgreSQL",
    "Docker", "AWS", "Git", "REST API", "GraphQL", "MongoDB", "Java", "C++",
    "Machine Learning", "Data Analysis", "Figma", "Photoshop"
  ],
  soft: [
    "Communication", "Leadership", "Problem Solving", "Teamwork", "Time Management",
    "Critical Thinking", "Adaptability", "Creativity", "Attention to Detail"
  ],
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function AIResumeBuilderPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedTemplate, setSelectedTemplate] = useState("modern");
  const [selectedTone, setSelectedTone] = useState("professional");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGenerated, setIsGenerated] = useState(false);
  const [previewZoom, setPreviewZoom] = useState(100);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [skillInput, setSkillInput] = useState({ technical: "", soft: "" });

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    trigger,
    formState: { errors, isValid },
  } = useForm<ResumeFormData>({
    resolver: zodResolver(resumeSchema),
    mode: "onChange",
    defaultValues: {
      fullName: "",
      email: "",
      phone: "",
      location: "",
      professionalTitle: "",
      linkedinUrl: "",
      portfolioUrl: "",
      experiences: [
        {
          company: "",
          position: "",
          startDate: "",
          endDate: "",
          isCurrent: false,
          description: "",
        },
      ],
      education: [
        { institution: "", degree: "", field: "", year: "" },
      ],
      technicalSkills: [],
      softSkills: [],
      languages: [{ name: "", proficiency: "" }],
      certifications: [],
      projects: [],
    },
  });

  const formData = watch();

  // Field arrays
  const {
    fields: experienceFields,
    append: appendExperience,
    remove: removeExperience,
  } = useFieldArray({ control, name: "experiences" });

  const {
    fields: educationFields,
    append: appendEducation,
    remove: removeEducation,
  } = useFieldArray({ control, name: "education" });

  const {
    fields: languageFields,
    append: appendLanguage,
    remove: removeLanguage,
  } = useFieldArray({ control, name: "languages" });

  const {
    fields: certificationFields,
    append: appendCertification,
    remove: removeCertification,
  } = useFieldArray({ control, name: "certifications" });

  const {
    fields: projectFields,
    append: appendProject,
    remove: removeProject,
  } = useFieldArray({ control, name: "projects" });

  // Auto-save effect
  useEffect(() => {
    const autoSave = setInterval(() => {
      localStorage.setItem("resume_draft", JSON.stringify(formData));
      setLastSaved(new Date());
    }, 30000); // 30 seconds

    return () => clearInterval(autoSave);
  }, [formData]);

  // Load saved draft
  useEffect(() => {
    const saved = localStorage.getItem("resume_draft");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        Object.keys(parsed).forEach((key) => {
          setValue(key as any, parsed[key]);
        });
      } catch (e) {
        console.error("Failed to load draft");
      }
    }
  }, []);

  // Step validation
  const validateCurrentStep = async () => {
    let fieldsToValidate: string[] = [];
    switch (currentStep) {
      case 1:
        fieldsToValidate = ["fullName", "email", "phone", "professionalTitle"];
        break;
      case 2:
        fieldsToValidate = ["experiences"];
        break;
      case 3:
        fieldsToValidate = ["education"];
        break;
      case 4:
        fieldsToValidate = ["technicalSkills", "softSkills"];
        break;
      case 5:
        return true;
    }
    return await trigger(fieldsToValidate as any);
  };

  const nextStep = async () => {
    const isValid = await validateCurrentStep();
    if (isValid && currentStep < 5) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  // Add skill
  const addSkill = (type: "technical" | "soft") => {
    const value = skillInput[type].trim();
    if (value) {
      const currentSkills = formData[type === "technical" ? "technicalSkills" : "softSkills"] || [];
      if (!currentSkills.includes(value)) {
        setValue(
          type === "technical" ? "technicalSkills" : "softSkills",
          [...currentSkills, value]
        );
      }
      setSkillInput((prev) => ({ ...prev, [type]: "" }));
    }
  };

  // Remove skill
  const removeSkill = (type: "technical" | "soft", skill: string) => {
    const field = type === "technical" ? "technicalSkills" : "softSkills";
    const currentSkills = formData[field] || [];
    setValue(field, currentSkills.filter((s) => s !== skill));
  };

  // Generate Resume
  const handleGenerate = async () => {
    setIsGenerating(true);

    // Simulate AI generation
    await new Promise((resolve) => setTimeout(resolve, 3000));

    setIsGenerating(false);
    setIsGenerated(true);

    // Confetti!
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ["#a855f7", "#6366f1", "#06b6d4"],
    });
  };

  // Progress calculation
  const progress = (currentStep / steps.length) * 100;

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* LEFT SIDE - Form (40%) */}
      <div className="w-full lg:w-[40%] flex flex-col border-r border-surface-200 dark:border-surface-700 overflow-hidden">
        {/* Header */}
        <div className="flex-shrink-0 border-b border-surface-200 bg-white p-4 dark:border-surface-700 dark:bg-surface-900">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-display text-xl font-bold text-surface-900 dark:text-white">
                AI Resume Builder
              </h1>
              <p className="text-sm text-surface-500">
                {steps[currentStep - 1].description}
              </p>
            </div>
            {lastSaved && (
              <span className="flex items-center gap-1 text-xs text-surface-400">
                <Save className="h-3 w-3" />
                Saved {lastSaved.toLocaleTimeString()}
              </span>
            )}
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="mb-2 flex justify-between text-xs">
              <span>Step {currentStep} of {steps.length}</span>
              <span>{Math.round(progress)}% complete</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          {/* Step Indicators */}
          <div className="mt-4 flex gap-2">
            {steps.map((step) => (
              <button
                key={step.id}
                onClick={() => setCurrentStep(step.id)}
                className={cn(
                  "flex flex-1 flex-col items-center gap-1 rounded-lg p-2 text-xs transition-all",
                  currentStep === step.id
                    ? "bg-purple-100 text-purple-700"
                    : currentStep > step.id
                    ? "bg-green-100 text-green-700"
                    : "bg-surface-100 text-surface-500"
                )}
              >
                <step.icon className="h-4 w-4" />
                <span className="hidden sm:block">{step.title}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Form Content */}
        <div className="flex-1 overflow-y-auto p-4">
          <AnimatePresence mode="wait">
            {/* Step 1: Personal Info */}
            {currentStep === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-4"
              >
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="sm:col-span-2">
                    <Label htmlFor="fullName">Full Name *</Label>
                    <Input
                      id="fullName"
                      placeholder="John Doe"
                      icon={<User className="h-4 w-4" />}
                      error={errors.fullName?.message}
                      {...register("fullName")}
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="john@example.com"
                      icon={<Mail className="h-4 w-4" />}
                      error={errors.email?.message}
                      {...register("email")}
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone *</Label>
                    <Input
                      id="phone"
                      placeholder="+998 90 123 4567"
                      icon={<Phone className="h-4 w-4" />}
                      error={errors.phone?.message}
                      {...register("phone")}
                    />
                  </div>
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      placeholder="Tashkent, Uzbekistan"
                      icon={<MapPin className="h-4 w-4" />}
                      {...register("location")}
                    />
                  </div>
                  <div>
                    <Label htmlFor="professionalTitle">Professional Title *</Label>
                    <Input
                      id="professionalTitle"
                      placeholder="Senior Software Engineer"
                      icon={<Briefcase className="h-4 w-4" />}
                      error={errors.professionalTitle?.message}
                      {...register("professionalTitle")}
                    />
                  </div>
                  <div>
                    <Label htmlFor="linkedinUrl">LinkedIn URL</Label>
                    <Input
                      id="linkedinUrl"
                      placeholder="https://linkedin.com/in/..."
                      icon={<Linkedin className="h-4 w-4" />}
                      {...register("linkedinUrl")}
                    />
                  </div>
                  <div>
                    <Label htmlFor="portfolioUrl">Portfolio / Website</Label>
                    <Input
                      id="portfolioUrl"
                      placeholder="https://yoursite.com"
                      icon={<Globe className="h-4 w-4" />}
                      {...register("portfolioUrl")}
                    />
                  </div>
                </div>
              </motion.div>
            )}

            {/* Step 2: Experience */}
            {currentStep === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {experienceFields.map((field, index) => (
                  <div
                    key={field.id}
                    className="relative rounded-xl border border-surface-200 p-4 dark:border-surface-700"
                  >
                    {experienceFields.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeExperience(index)}
                        className="absolute right-2 top-2 rounded-lg p-1 text-surface-400 hover:bg-red-50 hover:text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}

                    <div className="grid gap-4 sm:grid-cols-2">
                      <div>
                        <Label>Company Name *</Label>
                        <Input
                          placeholder="Acme Inc."
                          {...register(`experiences.${index}.company`)}
                        />
                      </div>
                      <div>
                        <Label>Position *</Label>
                        <Input
                          placeholder="Software Engineer"
                          {...register(`experiences.${index}.position`)}
                        />
                      </div>
                      <div>
                        <Label>Start Date *</Label>
                        <Input
                          type="month"
                          {...register(`experiences.${index}.startDate`)}
                        />
                      </div>
                      <div>
                        <Label>End Date</Label>
                        <Input
                          type="month"
                          placeholder="Present"
                          disabled={formData.experiences?.[index]?.isCurrent}
                          {...register(`experiences.${index}.endDate`)}
                        />
                        <label className="mt-2 flex items-center gap-2 text-sm">
                          <input
                            type="checkbox"
                            {...register(`experiences.${index}.isCurrent`)}
                            className="rounded border-surface-300"
                          />
                          Currently working here
                        </label>
                      </div>
                      <div className="sm:col-span-2">
                        <Label>Description *</Label>
                        <Textarea
                          placeholder="Describe your responsibilities and achievements..."
                          rows={4}
                          {...register(`experiences.${index}.description`)}
                        />
                      </div>
                    </div>
                  </div>
                ))}

                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() =>
                    appendExperience({
                      company: "",
                      position: "",
                      startDate: "",
                      endDate: "",
                      isCurrent: false,
                      description: "",
                    })
                  }
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Add Experience
                </Button>
              </motion.div>
            )}

            {/* Step 3: Education */}
            {currentStep === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {educationFields.map((field, index) => (
                  <div
                    key={field.id}
                    className="relative rounded-xl border border-surface-200 p-4 dark:border-surface-700"
                  >
                    {educationFields.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeEducation(index)}
                        className="absolute right-2 top-2 rounded-lg p-1 text-surface-400 hover:bg-red-50 hover:text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}

                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="sm:col-span-2">
                        <Label>Institution *</Label>
                        <Input
                          placeholder="University of..."
                          {...register(`education.${index}.institution`)}
                        />
                      </div>
                      <div>
                        <Label>Degree *</Label>
                        <Input
                          placeholder="Bachelor's"
                          {...register(`education.${index}.degree`)}
                        />
                      </div>
                      <div>
                        <Label>Field of Study *</Label>
                        <Input
                          placeholder="Computer Science"
                          {...register(`education.${index}.field`)}
                        />
                      </div>
                      <div>
                        <Label>Graduation Year *</Label>
                        <Input
                          placeholder="2024"
                          {...register(`education.${index}.year`)}
                        />
                      </div>
                    </div>
                  </div>
                ))}

                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() =>
                    appendEducation({
                      institution: "",
                      degree: "",
                      field: "",
                      year: "",
                    })
                  }
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Add Education
                </Button>
              </motion.div>
            )}

            {/* Step 4: Skills */}
            {currentStep === 4 && (
              <motion.div
                key="step4"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {/* Technical Skills */}
                <div>
                  <Label>Technical Skills</Label>
                  <div className="mt-2 flex gap-2">
                    <Input
                      placeholder="Add a skill..."
                      value={skillInput.technical}
                      onChange={(e) =>
                        setSkillInput((prev) => ({ ...prev, technical: e.target.value }))
                      }
                      onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addSkill("technical"))}
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => addSkill("technical")}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {formData.technicalSkills?.map((skill) => (
                      <Badge
                        key={skill}
                        variant="secondary"
                        className="cursor-pointer hover:bg-red-100 hover:text-red-700"
                        onClick={() => removeSkill("technical", skill)}
                      >
                        {skill} ×
                      </Badge>
                    ))}
                  </div>
                  <div className="mt-2">
                    <p className="text-xs text-surface-500 mb-2">Suggested skills:</p>
                    <div className="flex flex-wrap gap-1">
                      {commonSkills.technical
                        .filter((s) => !formData.technicalSkills?.includes(s))
                        .slice(0, 10)
                        .map((skill) => (
                          <button
                            key={skill}
                            type="button"
                            onClick={() =>
                              setValue("technicalSkills", [
                                ...(formData.technicalSkills || []),
                                skill,
                              ])
                            }
                            className="rounded-full border border-surface-200 px-2 py-0.5 text-xs text-surface-600 hover:border-purple-300 hover:bg-purple-50"
                          >
                            + {skill}
                          </button>
                        ))}
                    </div>
                  </div>
                </div>

                {/* Soft Skills */}
                <div>
                  <Label>Soft Skills</Label>
                  <div className="mt-2 flex gap-2">
                    <Input
                      placeholder="Add a skill..."
                      value={skillInput.soft}
                      onChange={(e) =>
                        setSkillInput((prev) => ({ ...prev, soft: e.target.value }))
                      }
                      onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addSkill("soft"))}
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => addSkill("soft")}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {formData.softSkills?.map((skill) => (
                      <Badge
                        key={skill}
                        variant="secondary"
                        className="cursor-pointer hover:bg-red-100 hover:text-red-700"
                        onClick={() => removeSkill("soft", skill)}
                      >
                        {skill} ×
                      </Badge>
                    ))}
                  </div>
                  <div className="mt-2">
                    <p className="text-xs text-surface-500 mb-2">Suggested skills:</p>
                    <div className="flex flex-wrap gap-1">
                      {commonSkills.soft
                        .filter((s) => !formData.softSkills?.includes(s))
                        .map((skill) => (
                          <button
                            key={skill}
                            type="button"
                            onClick={() =>
                              setValue("softSkills", [
                                ...(formData.softSkills || []),
                                skill,
                              ])
                            }
                            className="rounded-full border border-surface-200 px-2 py-0.5 text-xs text-surface-600 hover:border-purple-300 hover:bg-purple-50"
                          >
                            + {skill}
                          </button>
                        ))}
                    </div>
                  </div>
                </div>

                {/* Languages */}
                <div>
                  <Label>Languages</Label>
                  <div className="mt-2 space-y-2">
                    {languageFields.map((field, index) => (
                      <div key={field.id} className="flex gap-2">
                        <Input
                          placeholder="Language"
                          {...register(`languages.${index}.name`)}
                        />
                        <Select
                          value={formData.languages?.[index]?.proficiency}
                          onValueChange={(v) =>
                            setValue(`languages.${index}.proficiency`, v)
                          }
                        >
                          <SelectTrigger className="w-40">
                            <SelectValue placeholder="Level" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="native">Native</SelectItem>
                            <SelectItem value="fluent">Fluent</SelectItem>
                            <SelectItem value="advanced">Advanced</SelectItem>
                            <SelectItem value="intermediate">Intermediate</SelectItem>
                            <SelectItem value="basic">Basic</SelectItem>
                          </SelectContent>
                        </Select>
                        {languageFields.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={() => removeLanguage(index)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => appendLanguage({ name: "", proficiency: "" })}
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      Add Language
                    </Button>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Step 5: Additional */}
            {currentStep === 5 && (
              <motion.div
                key="step5"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {/* Template Selection */}
                <div>
                  <Label className="flex items-center gap-2">
                    <Palette className="h-4 w-4" />
                    Resume Template
                  </Label>
                  <div className="mt-2 grid grid-cols-2 gap-2">
                    {templates.map((template) => (
                      <button
                        key={template.id}
                        type="button"
                        onClick={() => setSelectedTemplate(template.id)}
                        className={cn(
                          "rounded-xl border-2 p-3 text-left transition-all",
                          selectedTemplate === template.id
                            ? "border-purple-500 bg-purple-50"
                            : "border-surface-200 hover:border-surface-300"
                        )}
                      >
                        <p className="font-medium text-surface-900">{template.name}</p>
                        <p className="text-xs text-surface-500">{template.description}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Tone Selection */}
                <div>
                  <Label className="flex items-center gap-2">
                    <Type className="h-4 w-4" />
                    Writing Tone
                  </Label>
                  <div className="mt-2 grid grid-cols-2 gap-2">
                    {tones.map((tone) => (
                      <button
                        key={tone.id}
                        type="button"
                        onClick={() => setSelectedTone(tone.id)}
                        className={cn(
                          "rounded-xl border-2 p-3 text-left transition-all",
                          selectedTone === tone.id
                            ? "border-purple-500 bg-purple-50"
                            : "border-surface-200 hover:border-surface-300"
                        )}
                      >
                        <p className="font-medium text-surface-900">{tone.name}</p>
                        <p className="text-xs text-surface-500">{tone.description}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Certifications */}
                <div>
                  <Label>Certifications (Optional)</Label>
                  <div className="mt-2 space-y-2">
                    {certificationFields.map((field, index) => (
                      <div key={field.id} className="flex gap-2">
                        <Input
                          placeholder="Certification name"
                          {...register(`certifications.${index}.name`)}
                        />
                        <Input
                          placeholder="Issuer"
                          className="w-32"
                          {...register(`certifications.${index}.issuer`)}
                        />
                        <Input
                          placeholder="Year"
                          className="w-20"
                          {...register(`certifications.${index}.year`)}
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removeCertification(index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        appendCertification({ name: "", issuer: "", year: "" })
                      }
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      Add Certification
                    </Button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 border-t border-surface-200 bg-white p-4 dark:border-surface-700 dark:bg-surface-900">
          <div className="flex gap-3">
            {currentStep > 1 && (
              <Button variant="outline" onClick={prevStep} className="flex-1">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Previous
              </Button>
            )}

            {currentStep < 5 ? (
              <Button
                onClick={nextStep}
                className="flex-1 bg-gradient-to-r from-purple-500 to-indigo-600"
              >
                Next
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="flex-1 bg-gradient-to-r from-purple-500 to-indigo-600 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Wand2 className="mr-2 h-4 w-4" />
                    Generate with AI
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* RIGHT SIDE - Preview (60%) */}
      <div className="hidden lg:flex lg:w-[60%] flex-col bg-surface-100 dark:bg-surface-800">
        {/* Preview Header */}
        <div className="flex items-center justify-between border-b border-surface-200 bg-white p-4 dark:border-surface-700 dark:bg-surface-900">
          <div className="flex items-center gap-2">
            <Eye className="h-5 w-5 text-surface-500" />
            <span className="font-medium text-surface-900 dark:text-white">Live Preview</span>
          </div>
          <div className="flex items-center gap-2">
            {/* Zoom controls */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setPreviewZoom((z) => Math.max(50, z - 10))}
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            <span className="text-sm text-surface-500 w-12 text-center">{previewZoom}%</span>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setPreviewZoom((z) => Math.min(150, z + 10))}
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
            <div className="mx-2 h-6 w-px bg-surface-200" />
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Download PDF
            </Button>
          </div>
        </div>

        {/* Preview Content */}
        <div className="flex-1 overflow-auto p-8">
          <div
            className="mx-auto bg-white shadow-2xl transition-transform"
            style={{
              transform: `scale(${previewZoom / 100})`,
              transformOrigin: "top center",
              width: "210mm",
              minHeight: "297mm",
            }}
          >
            {/* Resume Preview - Modern Template */}
            <div className="p-8">
              {/* Header */}
              <div className="border-b-2 border-purple-500 pb-6">
                <h1 className="text-3xl font-bold text-surface-900">
                  {formData.fullName || "Your Name"}
                </h1>
                <p className="mt-1 text-xl text-purple-600">
                  {formData.professionalTitle || "Professional Title"}
                </p>
                <div className="mt-4 flex flex-wrap gap-4 text-sm text-surface-600">
                  {formData.email && (
                    <span className="flex items-center gap-1">
                      <Mail className="h-4 w-4" /> {formData.email}
                    </span>
                  )}
                  {formData.phone && (
                    <span className="flex items-center gap-1">
                      <Phone className="h-4 w-4" /> {formData.phone}
                    </span>
                  )}
                  {formData.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" /> {formData.location}
                    </span>
                  )}
                </div>
              </div>

              {/* Experience */}
              {formData.experiences?.some((e) => e.company) && (
                <div className="mt-6">
                  <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-surface-900">
                    <Briefcase className="h-5 w-5 text-purple-500" />
                    Experience
                  </h2>
                  <div className="space-y-4">
                    {formData.experiences
                      .filter((e) => e.company)
                      .map((exp, i) => (
                        <div key={i} className="border-l-2 border-purple-200 pl-4">
                          <h3 className="font-semibold text-surface-900">{exp.position}</h3>
                          <p className="text-purple-600">{exp.company}</p>
                          <p className="text-sm text-surface-500">
                            {exp.startDate} - {exp.isCurrent ? "Present" : exp.endDate}
                          </p>
                          <p className="mt-2 text-sm text-surface-600">{exp.description}</p>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Education */}
              {formData.education?.some((e) => e.institution) && (
                <div className="mt-6">
                  <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-surface-900">
                    <GraduationCap className="h-5 w-5 text-purple-500" />
                    Education
                  </h2>
                  <div className="space-y-4">
                    {formData.education
                      .filter((e) => e.institution)
                      .map((edu, i) => (
                        <div key={i} className="border-l-2 border-purple-200 pl-4">
                          <h3 className="font-semibold text-surface-900">
                            {edu.degree} in {edu.field}
                          </h3>
                          <p className="text-purple-600">{edu.institution}</p>
                          <p className="text-sm text-surface-500">{edu.year}</p>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Skills */}
              {(formData.technicalSkills?.length > 0 || formData.softSkills?.length > 0) && (
                <div className="mt-6">
                  <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-surface-900">
                    <Code className="h-5 w-5 text-purple-500" />
                    Skills
                  </h2>
                  <div className="space-y-3">
                    {formData.technicalSkills?.length > 0 && (
                      <div>
                        <h3 className="text-sm font-medium text-surface-600">Technical</h3>
                        <div className="mt-1 flex flex-wrap gap-2">
                          {formData.technicalSkills.map((skill) => (
                            <span
                              key={skill}
                              className="rounded-full bg-purple-100 px-3 py-1 text-xs text-purple-700"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {formData.softSkills?.length > 0 && (
                      <div>
                        <h3 className="text-sm font-medium text-surface-600">Soft Skills</h3>
                        <div className="mt-1 flex flex-wrap gap-2">
                          {formData.softSkills.map((skill) => (
                            <span
                              key={skill}
                              className="rounded-full bg-cyan-100 px-3 py-1 text-xs text-cyan-700"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Placeholder when empty */}
              {!formData.fullName && (
                <div className="mt-8 flex flex-col items-center justify-center py-16 text-center">
                  <FileText className="h-16 w-16 text-surface-300" />
                  <p className="mt-4 text-lg font-medium text-surface-400">
                    Start filling the form to see your resume preview
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Success overlay */}
        <AnimatePresence>
          {isGenerated && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm"
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="rounded-2xl bg-white p-8 text-center shadow-2xl"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", delay: 0.2 }}
                  className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-green-100"
                >
                  <CheckCircle className="h-10 w-10 text-green-600" />
                </motion.div>
                <h2 className="font-display text-2xl font-bold text-surface-900">
                  Resume Generated! 🎉
                </h2>
                <p className="mt-2 text-surface-500">
                  Your AI-powered resume is ready
                </p>
                <div className="mt-6 flex gap-3">
                  <Button variant="outline" onClick={() => setIsGenerated(false)}>
                    Edit Resume
                  </Button>
                  <Button className="bg-gradient-to-r from-purple-500 to-indigo-600">
                    <Download className="mr-2 h-4 w-4" />
                    Download PDF
                  </Button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
















