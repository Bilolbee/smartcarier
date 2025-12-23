/**
 * Company Settings Page
 */

"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Building2,
  Mail,
  Phone,
  MapPin,
  Globe,
  Users,
  Camera,
  Save,
  Key,
  Bell,
  Trash2,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

const companySchema = z.object({
  company_name: z.string().min(2, "Company name is required"),
  company_description: z.string().max(2000).optional(),
  company_website: z.string().url("Invalid URL").optional().or(z.literal("")),
  company_size: z.string().optional(),
  company_industry: z.string().optional(),
  full_name: z.string().min(2, "Contact name is required"),
  email: z.string().email("Invalid email"),
  phone: z.string().optional(),
  location: z.string().optional(),
});

type CompanyFormData = z.infer<typeof companySchema>;

const companySizes = [
  { value: "1-10", label: "1-10 employees" },
  { value: "11-50", label: "11-50 employees" },
  { value: "51-200", label: "51-200 employees" },
  { value: "201-500", label: "201-500 employees" },
  { value: "501-1000", label: "501-1000 employees" },
  { value: "1000+", label: "1000+ employees" },
];

const industries = [
  "Technology",
  "Finance",
  "Healthcare",
  "Education",
  "Manufacturing",
  "Retail",
  "Media",
  "Consulting",
  "Real Estate",
  "Transportation",
  "Other",
];

export default function CompanySettingsPage() {
  const { user, updateUser, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState("company");

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isDirty },
  } = useForm<CompanyFormData>({
    resolver: zodResolver(companySchema),
    defaultValues: {
      company_name: user?.company_name || "",
      company_description: user?.company_description || "",
      company_website: user?.company_website || "",
      company_size: user?.company_size || "",
      company_industry: user?.company_industry || "",
      full_name: user?.full_name || "",
      email: user?.email || "",
      phone: user?.phone || "",
      location: user?.location || "",
    },
  });

  const onSubmit = async (data: CompanyFormData) => {
    try {
      await updateUser(data);
      toast.success("Settings updated successfully!");
    } catch (error) {
      toast.error("Failed to update settings");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-display text-2xl font-bold text-surface-900 dark:text-white">
          Company Settings
        </h1>
        <p className="mt-1 text-surface-500">
          Manage your company profile and account settings
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="company">Company Profile</TabsTrigger>
          <TabsTrigger value="account">Account</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>

        {/* Company Profile Tab */}
        <TabsContent value="company" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Company Information</CardTitle>
              <CardDescription>
                This information will be displayed on your job postings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {/* Logo */}
                <div className="flex items-center gap-4">
                  <div className="flex h-20 w-20 items-center justify-center rounded-xl bg-gradient-to-br from-brand-100 to-brand-200 dark:from-brand-900 dark:to-brand-800">
                    {user?.company_logo_url ? (
                      <img
                        src={user.company_logo_url}
                        alt={user.company_name || "Company"}
                        className="h-16 w-16 rounded-lg object-cover"
                      />
                    ) : (
                      <Building2 className="h-10 w-10 text-brand-600" />
                    )}
                  </div>
                  <div>
                    <Button variant="outline" size="sm">
                      <Camera className="mr-2 h-4 w-4" />
                      Upload Logo
                    </Button>
                    <p className="mt-1 text-xs text-surface-500">
                      Recommended: 200x200px, PNG or JPG
                    </p>
                  </div>
                </div>

                {/* Company Info */}
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="company_name">Company Name</Label>
                    <Input
                      id="company_name"
                      icon={<Building2 className="h-5 w-5" />}
                      error={errors.company_name?.message}
                      {...register("company_name")}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="company_website">Website</Label>
                    <Input
                      id="company_website"
                      icon={<Globe className="h-5 w-5" />}
                      placeholder="https://yourcompany.com"
                      error={errors.company_website?.message}
                      {...register("company_website")}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="company_size">Company Size</Label>
                    <Select
                      value={watch("company_size")}
                      onValueChange={(value) => setValue("company_size", value, { shouldDirty: true })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select size" />
                      </SelectTrigger>
                      <SelectContent>
                        {companySizes.map((size) => (
                          <SelectItem key={size.value} value={size.value}>
                            {size.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="company_industry">Industry</Label>
                    <Select
                      value={watch("company_industry")}
                      onValueChange={(value) => setValue("company_industry", value, { shouldDirty: true })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select industry" />
                      </SelectTrigger>
                      <SelectContent>
                        {industries.map((industry) => (
                          <SelectItem key={industry} value={industry}>
                            {industry}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      icon={<MapPin className="h-5 w-5" />}
                      placeholder="Tashkent, Uzbekistan"
                      error={errors.location?.message}
                      {...register("location")}
                    />
                  </div>
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="company_description">About Company</Label>
                  <Textarea
                    id="company_description"
                    placeholder="Tell candidates about your company, culture, and what makes you unique..."
                    className="min-h-[150px]"
                    error={errors.company_description?.message}
                    {...register("company_description")}
                  />
                </div>

                {/* Submit */}
                <div className="flex justify-end">
                  <Button type="submit" disabled={!isDirty} isLoading={isLoading}>
                    <Save className="mr-2 h-4 w-4" />
                    Save Changes
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Account Tab */}
        <TabsContent value="account" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Contact Information</CardTitle>
              <CardDescription>
                Primary contact for your company account
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="full_name">Contact Name</Label>
                    <Input
                      id="full_name"
                      error={errors.full_name?.message}
                      {...register("full_name")}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      icon={<Mail className="h-5 w-5" />}
                      error={errors.email?.message}
                      {...register("email")}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone</Label>
                    <Input
                      id="phone"
                      icon={<Phone className="h-5 w-5" />}
                      error={errors.phone?.message}
                      {...register("phone")}
                    />
                  </div>
                </div>
                <div className="flex justify-end">
                  <Button type="submit" disabled={!isDirty} isLoading={isLoading}>
                    <Save className="mr-2 h-4 w-4" />
                    Save Changes
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Change Password</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="current_password">Current Password</Label>
                  <Input id="current_password" type="password" icon={<Key className="h-5 w-5" />} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new_password">New Password</Label>
                  <Input id="new_password" type="password" icon={<Key className="h-5 w-5" />} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirm_password">Confirm New Password</Label>
                  <Input id="confirm_password" type="password" icon={<Key className="h-5 w-5" />} />
                </div>
                <Button>Update Password</Button>
              </form>
            </CardContent>
          </Card>

          <Card className="border-red-200 dark:border-red-800">
            <CardHeader>
              <CardTitle className="text-red-600">Danger Zone</CardTitle>
              <CardDescription>
                Permanently delete your company account
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="destructive">
                <Trash2 className="mr-2 h-4 w-4" />
                Delete Company Account
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Email Notifications</CardTitle>
              <CardDescription>
                Configure when you receive email notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                {
                  title: "New Applications",
                  description: "Get notified when someone applies to your jobs",
                },
                {
                  title: "Application Updates",
                  description: "When applicants withdraw or update their applications",
                },
                {
                  title: "Job Expiration",
                  description: "Reminders when your job postings are about to expire",
                },
                {
                  title: "Weekly Summary",
                  description: "Summary of applications and views for all jobs",
                },
              ].map((item, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between py-3 border-b border-surface-200 dark:border-surface-700 last:border-0"
                >
                  <div>
                    <p className="font-medium text-surface-900 dark:text-white">
                      {item.title}
                    </p>
                    <p className="text-sm text-surface-500">{item.description}</p>
                  </div>
                  <input
                    type="checkbox"
                    defaultChecked
                    className="h-5 w-5 rounded border-surface-300 text-brand-600 focus:ring-brand-500"
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
















