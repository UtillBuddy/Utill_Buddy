# Use an official Node.js runtime as a parent image
FROM node:20-slim

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files into the container at /app
COPY package*.json ./

# Install any needed packages specified in package.json
RUN npm install

# Copy the rest of the application's code into the container at /app
COPY . .

# Build the Next.js application
RUN npm run build

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run the Next.js application
CMD ["npm", "start"]
